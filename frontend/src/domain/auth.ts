export interface Credentials {
    email:string;
    password: string;
}


export interface AuthSession{
    access_token:string;
    token_type:"bearer";
    user_id:number;
    email:string;
    expires_at:number;
}