import requests

from src.constants import GQL_URL, RETRY_ERROR_CODES
from src.logger import setup_logger
from src.util import get_str_from_teams

log = setup_logger(__name__)


class GQLRequest:
    """This class is used to make requests to the GitHub GQL API"""
    def __init__(self, token, org, repo):
        self.token = token
        self.org = org
        self.repo = repo

    def make_ghl_request(self, data=None):
        """
        Makes a request to the GitHub GQL API
        Args:
            data: data to send in the request
        Returns: response object
        """
        try:
            payload = {
                "query": data
            }
            response = self.post_request(GQL_URL, payload)
            if response.get("data") is None:
                error_msg = f"API call failed with error: {response.get('errors')}"
                log.error(error_msg)
                raise Exception(error_msg)
            return response.get("data")
        except requests.exceptions.HTTPError as e:
            log.error(f"An error occurred: {e}")
            raise Exception(f"An error occurred: {e}")

    def create_branch_protection_rule(self, pattern, push_allowance_ids=None, bypass_force_push_ids=None):
        """
        Creates a branch protection rule with the specified pattern and permissions

        Args:
            pattern (str): The branch name pattern to protect (e.g., "main", "release/*")
            push_allowance_ids (list): List of user/team IDs who can push to this branch
            bypass_force_push_ids (list): List of user/team IDs who can force push to this branch

        Returns:
            dict: The created branch protection rule data
        """
        # First, get the repository ID
        repo_query = f"""
            query {{
                repository(owner: "{self.org}", name: "{self.repo}") {{
                    id
                }}
            }}
        """

        repo_response = self.make_ghl_request(repo_query)
        repository_id = repo_response.get("repository", {}).get("id")

        if not repository_id:
            error_msg = f"Could not find repository with owner '{self.org}' and name '{self.repo}'"
            log.error(error_msg)
            raise Exception(error_msg)

        # Format actor IDs for GraphQL
        push_ids_str = get_str_from_teams(push_allowance_ids)
        bypass_ids_str = get_str_from_teams(bypass_force_push_ids)

        # Create the mutation
        mutation = f"""
            mutation {{
                createBranchProtectionRule(input: {{
                    repositoryId: "{repository_id}",
                    pattern: "{pattern}",
                    restrictsPushes:true,
                    pushActorIds: {push_ids_str},
                    bypassForcePushActorIds: {bypass_ids_str}
                }}) {{
                    branchProtectionRule {{
                        id
                        pattern
                        pushAllowances(first: 10) {{
                            edges {{
                                node {{
                                    actor {{
                                        ... on User {{
                                            login
                                        }}
                                        ... on Team {{
                                            name
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        bypassForcePushAllowances(first: 10) {{
                            edges {{
                                node {{
                                    actor {{
                                        ... on User {{
                                            login
                                        }}
                                        ... on Team {{
                                            name
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        """

        response = self.make_ghl_request(mutation)

        if response and 'createBranchProtectionRule' in response:
            created_rule = response['createBranchProtectionRule']['branchProtectionRule']
            log.info(f"Branch protection rule created for pattern '{pattern}'")
            return created_rule
        else:
            error_msg = f"Failed to create branch protection rule for pattern '{pattern}'"
            log.error(error_msg)
            raise Exception(error_msg)

    def get_lrb_branch_protection_id(self):
        """
        This function is used to get the branch protection id for the LRB
        Returns: (str) the branch protection id
        """
        query = f"""
            query {{
                repository(owner: "{self.org}", name: "{self.repo}") {{
                    branchProtectionRules(first: 100) {{
                        edges {{
                            node {{
                                id
                                pattern
                            }}
                        }}
                    }}
                }}
            }}
        """
        response = self.make_ghl_request(query)
        edges = response.get("repository").get("branchProtectionRules").get("edges")
        for edge in edges:
            node = edge.get("node")
            if node.get("pattern") == "lrb/*":
                return node.get("id")

    def add_user_to_branch_protection_force_push(self, branch_protection_id, user_ids):
        """
        This function is used to add a user to the branch protection force push
        Args:
            branch_protection_id: branch protection id
            user_ids: list of user logins
        Returns: None
        """
        user_logins = get_str_from_teams(user_ids)
        mutation = f"""
            mutation {{
            updateBranchProtectionRule(input: {{
                branchProtectionRuleId: "{branch_protection_id}",
                bypassForcePushActorIds: {user_logins}
            }}) {{
                branchProtectionRule {{
                    id
                    bypassForcePushAllowances(first: 5) {{
                        edges {{
                            node {{
                                actor {{
                                    ... on User {{
                                        login
                                    }}
                                    ... on Team {{
                                        name
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        response = self.make_ghl_request(mutation)
        if response.get("updateBranchProtectionRule").get("branchProtectionRule").get("id") == branch_protection_id:
            log.info(f"User {user_logins} added to branch protection rule {branch_protection_id}")
        else:
            error_msg = f"Failed to add user {user_logins} to branch protection rule {branch_protection_id} - {response.get('errors')}"
            log.error(error_msg)
            Exception(error_msg)

    def post_request(self, url, data, retries=3):
        """ This method retries a post request if there are retryable errors
        Args:
            url: url endpoint
            data: data to send in the request
            retries: number of retries
        Returns: response object
        """
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = None
        for i in range(retries):
            requests.packages.urllib3.disable_warnings()
            response = requests.post(url, headers=headers, json=data)
            if response.status_code not in RETRY_ERROR_CODES:
                if response.status_code != 200:
                    log.error(f"API call failed for {url} with error: {response.text}")
                response.raise_for_status()  # Raise an exception for HTTP errors
                break
            else:
                log.warning(f'Try {i + 1}: \n status code: {response.status_code}\n response: {response.text}')

        return response.json()
