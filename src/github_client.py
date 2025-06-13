from requests import HTTPError
from src import logger
from src.http_request import HttpRequest

log = logger.setup_logger(__name__)

class GithubClient:
    def __init__(self, token, owner, repo):
        self.owner = owner
        self.repo_name = repo
        self.token = token
        self.http_request = HttpRequest( self.token, self.owner, self.repo_name)

    def update_branch_protection(self, branchName, payload):
        self.http_request.put(f"/branches/{branchName}/protection", payload)

    def create_repo_ruleset(self, payload):
        self.http_request.post("/rulesets", payload)

    def update_repo_sonar_ruleset(self, rulesetId):
        sonar_rule = {
            "type": "required_status_checks",
            "parameters": {
                "strict_required_status_checks_policy": True,
                "required_status_checks": None
            }
        }
        self.http_request.put(f"/rulesets/{rulesetId}", sonar_rule)

    def update_ruleset_property(self, rulesetId, key, value):
        # options are disabled, active, evaluate
        payload = {key: value}
        self.update_ruleset(rulesetId, payload)

    def update_ruleset(self, rulesetId, payload):
        self.http_request.put(f"/rulesets/{rulesetId}", payload)

    def delete_ruleset(self, rulesetId):
        self.http_request.delete(f"/rulesets/{rulesetId}")

    def get_repo_rulesets(self):
        try:
            return self.http_request.get(f"/rulesets")
        except HTTPError as http_error:
            if http_error.response.status_code == 404:
                return []

    def get_repo_ruleset_by_id(self, ruleset_id):
        try:
            return self.http_request.get(f"/rulesets/{ruleset_id}")
        except HTTPError as http_error:
            if http_error.response.status_code == 404:
                return None

    def get_repo_ruleset_by_name(self, ruleset_name):
        rulesets = self.get_repo_rulesets()
        for ruleset in rulesets:
            if ruleset.get("name") == ruleset_name:
                return self.get_repo_ruleset_by_id(ruleset.get("id", None))
        return None
    
    def create_repo_from_template(self, payload, template):
        url_segment = f"/generate"
        try:
            template_http = HttpRequest(owner=self.owner, repo_name=template, github_token=self.token)
            response = template_http.post(url_segment, payload)
            log.info(f"Successfully created repository '{self.repo_name}.")
            return response.json()
        except Exception as err:
            log.error(f"Error creating repository '{self.repo_name}': {err}")

    def add_ruleset(self, payload, ruleset_name):
        url_segment = f"/rulesets"
        try:
            self.http_request.post(url_segment, payload)
            log.info(f"Successfully added ruleset '{ruleset_name}' to repository '{self.repo_name}'.")
        except Exception as err:
            log.error(f"Error adding ruleset '{ruleset_name}' to repository '{self.repo_name}': {err}")

    def get_team_id(self, team_slug):
        url_segment = f"/teams/{team_slug}"
        try:
            response = self.http_request.org_get_request(url_segment)
            return response.get("id")
        except Exception as err:
            log.error(f"Error fetching ID for team '{team_slug}': {err}")
            return None

    def add_collaborators(self, teams):
        for team, permission in teams.items():
            url_segment = f"/teams/{team}/repos/{self.owner}/{self.repo_name}"
            payload = {"permission": permission}
            try:
                self.http_request.org_put_request(url_segment, payload)
                log.info(f"Successfully added team '{team}' with '{permission}' permission to repository '{self.repo_name}'.")
            except Exception as err:
                log.error(f"Error adding team '{team}' to repository '{self.repo_name}': {err}")
