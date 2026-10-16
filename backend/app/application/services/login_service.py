from email_validator import EmailNotValidError, validate_email
from app.application.ports.login_use_case import InvalidCredentialsError
from app.application.ports.password_hasher_port import PasswordHasherPort
from app.application.ports.token_issuer_port import TokenIssuerPort
from app.domain.ports.user_repository_port import  UserRepositoryPort


class LoginService:
    def __init__(self, repository:UserRepositoryPort, password_verifier:PasswordHasherPort, token:TokenIssuerPort)-> None:
        self.repository= repository
        self.password_verifier= password_verifier
        self.token= token

    async def execute(self, email:str, password:str)->str:
        try:
            email = validate_email(
                email.strip(), check_deliverability=False
            ).normalized.lower()
        except EmailNotValidError as exc:
            raise InvalidCredentialsError from exc
        user= await self.repository.get_by_email(email)
        valid = await self.password_verifier.verify_password(password,user.password_hash if user is not None else None)
        if user is None or not valid:
            raise InvalidCredentialsError
        if user.user_id is None:
            raise RuntimeError("Persisted user has no ID")

        return self.token.issue(user.user_id)
    