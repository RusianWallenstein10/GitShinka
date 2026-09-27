import requests
from typing import Dict, Any, Optional, List
from core.ports.github_client import GithubClient

class HttpGithubClient(GithubClient):
    def __init__(self, base_url: str = "https://api.github.com"):
        self.base_url = base_url

    def _get_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_summary_metrics(self, token: str) -> Dict[str, Any]:
        if not token:
            return {"error": "No GitHub Token found"}
            
        try:
            headers = self._get_headers(token)
            user_response = requests.get(f"{self.base_url}/user", headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            repos_response = requests.get(f"{self.base_url}/user/repos?per_page=100&type=owner&sort=updated", headers=headers)
            repos_response.raise_for_status()
            repos = repos_response.json()
            
            total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
            total_forks = sum(repo.get("forks_count", 0) for repo in repos)
            
            repo_list = []
            for r in repos:
                repo_list.append({
                    "name": r.get("name"),
                    "private": r.get("private"),
                    "language": r.get("language") or "N/A",
                    "updated_at": r.get("updated_at"),
                    "stars": r.get("stargazers_count", 0),
                    "url": r.get("html_url")
                })
            
            return {
                "username": user_data.get("login"),
                "name": user_data.get("name"),
                "avatar_url": user_data.get("avatar_url"),
                "public_repos": user_data.get("public_repos"),
                "private_repos": user_data.get("total_private_repos", 0),
                "total_stars": total_stars,
                "total_forks": total_forks,
                "followers": user_data.get("followers"),
                "repos": repo_list
            }
        except Exception as e:
            return {"error": str(e)}

    def get_other_user_metrics(self, token: str, username: str) -> Dict[str, Any]:
        if not token:
            return {"error": "No GitHub Token found"}
            
        try:
            headers = self._get_headers(token)
            user_response = requests.get(f"{self.base_url}/users/{username}", headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            repos_response = requests.get(f"{self.base_url}/users/{username}/repos?per_page=100&type=owner&sort=updated", headers=headers)
            repos_response.raise_for_status()
            repos = repos_response.json()
            
            total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
            total_forks = sum(repo.get("forks_count", 0) for repo in repos)
            
            repo_list = []
            for r in repos:
                repo_list.append({
                    "name": r.get("name"),
                    "private": r.get("private"),
                    "language": r.get("language") or "N/A",
                    "updated_at": r.get("updated_at"),
                    "stars": r.get("stargazers_count", 0),
                    "url": r.get("html_url")
                })
            
            return {
                "username": user_data.get("login"),
                "name": user_data.get("name"),
                "avatar_url": user_data.get("avatar_url"),
                "public_repos": user_data.get("public_repos"),
                "private_repos": 0,
                "total_stars": total_stars,
                "total_forks": total_forks,
                "followers": user_data.get("followers"),
                "repos": repo_list
            }
        except Exception as e:
            return {"error": str(e)}

    def get_repo_details(self, token: str, username: str, repo_name: str) -> Dict[str, Any]:
        if not token:
            return {"error": "No GitHub Token found"}
            
        try:
            headers = self._get_headers(token)
            
            commits_response = requests.get(f"{self.base_url}/repos/{username}/{repo_name}/commits?per_page=100", headers=headers)
            commits_data = commits_response.json() if commits_response.status_code == 200 else []
            
            issues_response = requests.get(f"{self.base_url}/repos/{username}/{repo_name}/issues?state=all&per_page=100", headers=headers)
            issues_data = issues_response.json() if issues_response.status_code == 200 else []
            
            repo_response = requests.get(f"{self.base_url}/repos/{username}/{repo_name}", headers=headers)
            repo_data = repo_response.json() if repo_response.status_code == 200 else {}
            
            prs_response = requests.get(f"{self.base_url}/repos/{username}/{repo_name}/pulls?state=all&per_page=100", headers=headers)
            prs_data = prs_response.json() if prs_response.status_code == 200 else []
            
            langs_response = requests.get(f"{self.base_url}/repos/{username}/{repo_name}/languages", headers=headers)
            langs_data = langs_response.json() if langs_response.status_code == 200 else {}
            
            workflows_response = requests.get(f"{self.base_url}/repos/{username}/{repo_name}/contents/.github/workflows", headers=headers)
            has_ci_cd = workflows_response.status_code == 200 and isinstance(workflows_response.json(), list)
            
            authors = {}
            commit_dates = {}
            recent_commits = []
            
            if isinstance(commits_data, list):
                for idx, c in enumerate(commits_data):
                    commit_info = c.get("commit", {})
                    author_name = commit_info.get("author", {}).get("name", "Unknown")
                    date_str = commit_info.get("author", {}).get("date")
                    msg = commit_info.get("message", "")
                    url = c.get("html_url", "")
                    
                    if date_str:
                        day = date_str[:10]
                        commit_dates[day] = commit_dates.get(day, 0) + 1
                    
                    authors[author_name] = authors.get(author_name, 0) + 1
                    
                    if idx < 5:
                        recent_commits.append({
                            "author": author_name,
                            "date": date_str,
                            "message": msg,
                            "url": url
                        })
                    
            open_issues = 0
            closed_issues = 0
            if isinstance(issues_data, list):
                for i in issues_data:
                    if "pull_request" not in i:
                        if i.get("state") == "open":
                            open_issues += 1
                        else:
                            closed_issues += 1
                            
            open_prs = 0
            merged_prs = 0
            if isinstance(prs_data, list):
                for pr in prs_data:
                    if pr.get("state") == "open":
                        open_prs += 1
                    elif pr.get("merged_at"):
                        merged_prs += 1
                        
            total_bytes = sum(langs_data.values()) if langs_data else 0
            languages = {}
            if total_bytes > 0:
                for lang, b in langs_data.items():
                    languages[lang] = round((b / total_bytes) * 100, 1)
            
            sorted_commit_dates = [{"date": k, "count": v} for k, v in sorted(commit_dates.items())]
            
            return {
                "name": repo_data.get("name", repo_name),
                "language": repo_data.get("language", "N/A"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "total_commits": len(commits_data) if isinstance(commits_data, list) else 0,
                "authors": authors,
                "commit_dates": sorted_commit_dates,
                "recent_commits": recent_commits,
                "open_issues": open_issues,
                "closed_issues": closed_issues,
                "open_prs": open_prs,
                "merged_prs": merged_prs,
                "has_ci_cd": has_ci_cd,
                "languages": languages,
                "has_projects": repo_data.get("has_projects", False),
                "url": repo_data.get("html_url")
            }
        except Exception as e:
            return {"error": str(e)}

    def search_github(self, token: str, query: str, search_type: str = "users") -> Dict[str, Any]:
        if not token:
            return {"error": "No GitHub Token found"}
            
        try:
            headers = self._get_headers(token)
            if search_type == "users":
                url = f"{self.base_url}/search/users?q={query}&per_page=12"
            else:
                url = f"{self.base_url}/search/repositories?q={query}&per_page=12"
                
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if search_type == "users":
                for item in data.get("items", []):
                    results.append({
                        "id": item.get("id"),
                        "username": item.get("login"),
                        "avatar_url": item.get("avatar_url"),
                        "url": item.get("html_url"),
                        "type": item.get("type")
                    })
            else:
                for item in data.get("items", []):
                    results.append({
                        "id": item.get("id"),
                        "name": item.get("full_name"),
                        "description": item.get("description"),
                        "stars": item.get("stargazers_count"),
                        "language": item.get("language") or "N/A",
                        "url": item.get("html_url"),
                        "owner_avatar": item.get("owner", {}).get("avatar_url")
                    })
                    
            return {
                "total_count": data.get("total_count", 0),
                "items": results
            }
        except Exception as e:
            return {"error": str(e)}

    def exchange_code_for_token(self, client_id: str, client_secret: str, code: str) -> Optional[str]:
        try:
            url = "https://github.com/login/oauth/access_token"
            headers = {"Accept": "application/json"}
            payload = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": "http://localhost:3000/callback"
            }
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                return f"ERROR:{data.get('error_description', data.get('error'))}"
            return data.get("access_token")
        except Exception as e:
            return f"ERROR:{str(e)}"

    def get_user_repos(self, username: str, token: str) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/users/{username}/repos?sort=pushed&per_page=100"
            headers = self._get_headers(token)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching repos for {username}: {e}")
            return []

    def create_issue(self, owner: str, repo: str, title: str, body: str, token: str) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            headers = self._get_headers(token)
            payload = {"title": title, "body": body}
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in (200, 201):
                return response.json()
            else:
                return {"error": f"Status {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
