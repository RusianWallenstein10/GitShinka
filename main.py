from fastapi import FastAPI, Depends, HTTPException, Query, Body
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

# Import Domain & Infrastructure
from infrastructure.database_setup import init_db
from infrastructure.adapters.sqlite_user_repository import SqliteUserRepository
from infrastructure.adapters.http_github_client import HttpGithubClient
from infrastructure.adapters.sqlite_classroom_repository import SqliteClassroomRepository
from core.use_cases.auth_use_cases import AuthUseCases
from core.use_cases.github_use_cases import GithubUseCases
from core.use_cases.classroom_use_cases import ClassroomUseCases
from core.use_cases.automation_use_cases import AutomationUseCases

load_dotenv()

tags_metadata = [
    {
        "name": "Autenticación",
        "description": "Operaciones con usuarios, registro e inicio de sesión en GitShinka.",
    },
    {
        "name": "GitHub",
        "description": "Integración con la API de GitHub, obtención de métricas, repositorios y búsquedas.",
    },
    {
        "name": "Classroom",
        "description": "Gestión de aulas virtuales y monitoreo de estudiantes.",
    },
]

app = FastAPI(
    title="GitShinka API", 
    description="Backend profesional para GitShinka Github Monitor, diseñado para ser fácilmente consumido por clientes externos.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Soporte GitShinka",
        "url": "http://github.com/GitShinka",
    },
)

# Allow CORS for Next.js frontend and any other integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
init_db()

# Dependency Injection
def get_auth_use_cases() -> AuthUseCases:
    repo = SqliteUserRepository()
    client = HttpGithubClient()
    return AuthUseCases(repo, client)

def get_github_use_cases() -> GithubUseCases:
    client = HttpGithubClient()
    return GithubUseCases(client)

def get_classroom_use_cases() -> ClassroomUseCases:
    repo = SqliteClassroomRepository()
    client = HttpGithubClient()
    return ClassroomUseCases(repo, client)

def get_automation_use_cases() -> AutomationUseCases:
    repo = SqliteClassroomRepository()
    client = HttpGithubClient()
    return AutomationUseCases(repo, client)

# Pydantic Models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    user_id: int

class AuthUrlResponse(BaseModel):
    url: str

class CallbackResponse(BaseModel):
    message: str

class RepoSummary(BaseModel):
    name: str
    private: bool
    language: str
    updated_at: str
    stars: int
    url: str

class DashboardResponse(BaseModel):
    username: str
    name: Optional[str]
    avatar_url: str
    public_repos: int
    private_repos: int
    total_stars: int
    total_forks: int
    followers: int
    repos: List[RepoSummary]

class ErrorResponse(BaseModel):
    detail: str

class CreateClassroomRequest(BaseModel):
    name: str

class AddStudentRequest(BaseModel):
    github_username: str

class DispatchIssueRequest(BaseModel):
    target_repo_name: str
    title: str
    body: str

class ClassroomResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    students: List[str]

@app.get("/", response_class=HTMLResponse, tags=["Inicio"])
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GitShinka API</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; }
            .bg-gradient { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); }
            .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
        </style>
    </head>
    <body class="bg-gradient text-white min-h-screen flex flex-col items-center justify-center p-6">
        <div class="max-w-4xl w-full glass-card rounded-2xl p-10 shadow-2xl">
            <div class="flex items-center justify-between border-b border-slate-700 pb-6 mb-8">
                <div>
                    <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 mb-2">
                        GitShinka API
                    </h1>
                    <p class="text-slate-400 text-lg">Backend de Monitoreo Analítico para GitHub</p>
                </div>
                <div class="text-right">
                    <span class="bg-blue-900/50 text-blue-300 text-xs font-semibold px-3 py-1 rounded-full border border-blue-800">
                        v1.0.0
                    </span>
                    <p class="text-slate-500 text-xs mt-2">Powered by <span class="text-teal-400 font-bold">FastAPI</span> ⚡</p>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div>
                    <h2 class="text-2xl font-bold mb-4 text-slate-200">🚀 Cómo Integrar</h2>
                    <p class="text-slate-400 mb-4 leading-relaxed">
                        Esta API está habilitada con <strong>CORS Universal</strong>, por lo que puedes consumirla desde cualquier frontend (React, Vue, Angular) o herramienta (Postman, cURL).
                    </p>
                    <div class="bg-slate-900 rounded-lg p-4 font-mono text-sm text-green-400 border border-slate-700 overflow-x-auto">
                        <span class="text-slate-500"># Ejemplo de uso con Fetch en JS</span><br>
                        fetch("http://127.0.0.1:8000/api/github/search?q=fastapi")<br>
                        &nbsp;&nbsp;.then(res => res.json())<br>
                        &nbsp;&nbsp;.then(data => console.log(data));
                    </div>
                </div>
                <div>
                    <h2 class="text-2xl font-bold mb-4 text-slate-200">📚 Documentación</h2>
                    <p class="text-slate-400 mb-6 leading-relaxed">
                        Explora nuestros endpoints, prueba la API en vivo y revisa los esquemas de datos exactos a través de nuestras interfaces interactivas:
                    </p>
                    <div class="flex flex-col gap-4">
                        <a href="/docs" class="flex items-center justify-center gap-2 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 px-6 py-3 rounded-lg font-semibold transition-all shadow-lg hover:shadow-teal-500/25">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            Abrir Swagger UI (Interactivo)
                        </a>
                        <a href="/redoc" class="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 px-6 py-3 rounded-lg font-semibold transition-all shadow-lg">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                            Abrir ReDoc (Detallado)
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="text-center text-slate-500 text-sm border-t border-slate-700 pt-6">
                GitShinka &copy; 2026. Diseñado para simplificar tus integraciones de GitHub.
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post(
    "/api/auth/login", 
    response_model=TokenResponse, 
    tags=["Autenticación"], 
    summary="Iniciar sesión",
    description="Inicia sesión con un usuario existente y devuelve el ID del usuario."
)
def login(req: LoginRequest, auth: AuthUseCases = Depends(get_auth_use_cases)):
    user_id = auth.login(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return TokenResponse(user_id=user_id)

@app.post(
    "/api/auth/register", 
    response_model=TokenResponse, 
    tags=["Autenticación"], 
    summary="Registrar usuario",
    description="Registra un nuevo usuario en la base de datos de GitShinka."
)
def register(req: RegisterRequest, auth: AuthUseCases = Depends(get_auth_use_cases)):
    user_id = auth.register(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return TokenResponse(user_id=user_id)

@app.get(
    "/api/github/auth-url", 
    response_model=AuthUrlResponse,
    tags=["GitHub"], 
    summary="Obtener URL de autorización OAuth",
    description="Genera la URL para redirigir al usuario y autorizar la aplicación en GitHub."
)
def get_auth_url(user_id: int):
    client_id = os.getenv("GITHUB_CLIENT_ID", "").strip()
    if not client_id:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID no está configurado")
    
    url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=repo,user&state={user_id}&redirect_uri=http://localhost:3000/callback"
    return AuthUrlResponse(url=url)

@app.post(
    "/api/github/callback", 
    response_model=CallbackResponse,
    tags=["GitHub"], 
    summary="Callback de OAuth",
    description="Endpoint al que redirige GitHub tras la autorización para intercambiar el código por un token de acceso."
)
def github_callback(
    code: str = Body(...), 
    state: str = Body(...), 
    auth: AuthUseCases = Depends(get_auth_use_cases)
):
    client_id = os.getenv("GITHUB_CLIENT_ID", "").strip()
    client_secret = os.getenv("GITHUB_CLIENT_SECRET", "").strip()
    
    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    result = auth.handle_github_oauth_callback(client_id, client_secret, code, user_id)
    if result != "SUCCESS":
        error_msg = result.replace("ERROR:", "") if result else "Error desconocido"
        raise HTTPException(status_code=400, detail=f"GitHub: {error_msg}")
    return CallbackResponse(message="Conectado exitosamente")

@app.get(
    "/api/github/dashboard", 
    response_model=DashboardResponse,
    tags=["GitHub"], 
    summary="Obtener resumen del Dashboard",
    description="Devuelve las métricas principales y repositorios recientes del usuario conectado a GitHub.",
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
def get_dashboard(user_id: int, auth: AuthUseCases = Depends(get_auth_use_cases), gh: GithubUseCases = Depends(get_github_use_cases)):
    token = auth.get_github_token(user_id)
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado con GitHub")
    
    metrics = gh.get_dashboard_summary(token)
    if "error" in metrics:
        if "401" in metrics["error"] or "Unauthorized" in metrics["error"]:
            raise HTTPException(status_code=401, detail="Token de GitHub expirado o inválido")
        raise HTTPException(status_code=400, detail=metrics["error"])
    return metrics

@app.get(
    "/api/github/search",
    tags=["GitHub"], 
    summary="Buscar en GitHub",
    description="Permite buscar repositorios o usuarios globales en GitHub.",
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
def search_github(
    user_id: int, 
    q: str = Query(..., description="Término de búsqueda"), 
    type: str = Query("users", description="Tipo de búsqueda: 'users' o 'repositories'"), 
    auth: AuthUseCases = Depends(get_auth_use_cases), 
    gh: GithubUseCases = Depends(get_github_use_cases)
):
    token = auth.get_github_token(user_id)
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado con GitHub")
    
    res = gh.search(token, q, type)
    if "error" in res:
        if "401" in res["error"] or "Unauthorized" in res["error"]:
            raise HTTPException(status_code=401, detail="Token de GitHub expirado o inválido")
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.get(
    "/api/github/repo",
    tags=["GitHub"], 
    summary="Obtener detalles de repositorio",
    description="Devuelve analíticas y métricas detalladas de un repositorio específico.",
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
def get_repo_details(
    user_id: int, 
    owner: str = Query(..., description="Propietario del repositorio"), 
    repo: str = Query(..., description="Nombre del repositorio"), 
    auth: AuthUseCases = Depends(get_auth_use_cases), 
    gh: GithubUseCases = Depends(get_github_use_cases)
):
    token = auth.get_github_token(user_id)
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado con GitHub")
    
    details = gh.get_repo_details(token, owner, repo)
    if "error" in details:
        if "401" in details["error"] or "Unauthorized" in details["error"]:
            raise HTTPException(status_code=401, detail="Token de GitHub expirado o inválido")
        raise HTTPException(status_code=400, detail=details["error"])
    return details

# --- Classroom Endpoints ---

@app.post(
    "/api/classrooms",
    response_model=ClassroomResponse,
    tags=["Classroom"],
    summary="Crear un Classroom",
    description="Crea una nueva aula virtual y la asocia al docente."
)
def create_classroom(
    req: CreateClassroomRequest,
    user_id: int = Query(...),
    cr: ClassroomUseCases = Depends(get_classroom_use_cases)
):
    cid = cr.create_classroom(req.name, user_id)
    if not cid:
        raise HTTPException(status_code=500, detail="Error creando el classroom")
    return ClassroomResponse(id=cid, name=req.name, teacher_id=user_id, students=[])

@app.get(
    "/api/classrooms",
    response_model=List[ClassroomResponse],
    tags=["Classroom"]
)
def get_classrooms(
    user_id: int = Query(...),
    cr: ClassroomUseCases = Depends(get_classroom_use_cases)
):
    classrooms = cr.get_classrooms_by_teacher(user_id)
    return [
        ClassroomResponse(
            id=c.id, 
            name=c.name, 
            teacher_id=c.teacher_id, 
            students=cr.get_classroom_by_id(c.id).students if cr.get_classroom_by_id(c.id) else []
        ) for c in classrooms
    ]

@app.post(
    "/api/classrooms/{classroom_id}/students",
    tags=["Classroom"]
)
def add_student(
    classroom_id: int,
    req: AddStudentRequest,
    cr: ClassroomUseCases = Depends(get_classroom_use_cases)
):
    success = cr.add_student_to_classroom(classroom_id, req.github_username)
    if not success:
        raise HTTPException(status_code=400, detail="El estudiante ya existe o hubo un error")
    return {"message": "Estudiante agregado"}

@app.get(
    "/api/classrooms/{classroom_id}/dashboard",
    tags=["Classroom"]
)
def get_classroom_dashboard(
    classroom_id: int,
    user_id: int = Query(...),
    auth: AuthUseCases = Depends(get_auth_use_cases),
    cr: ClassroomUseCases = Depends(get_classroom_use_cases)
):
    token = auth.get_github_token(user_id)
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado con GitHub")
        
    metrics = cr.get_classroom_metrics(classroom_id, token)
    if "error" in metrics:
        raise HTTPException(status_code=404, detail=metrics["error"])
    return metrics

# --- Automation Endpoints ---

@app.post(
    "/api/classrooms/{classroom_id}/automations/issues",
    tags=["Classroom"]
)
def dispatch_issue(
    classroom_id: int,
    req: DispatchIssueRequest,
    user_id: int = Query(...),
    auth: AuthUseCases = Depends(get_auth_use_cases),
    auto: AutomationUseCases = Depends(get_automation_use_cases)
):
    token = auth.get_github_token(user_id)
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado con GitHub")
    
    res = auto.dispatch_issue_to_classroom(
        classroom_id=classroom_id,
        target_repo_name=req.target_repo_name,
        title=req.title,
        body=req.body,
        teacher_token=token
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res
