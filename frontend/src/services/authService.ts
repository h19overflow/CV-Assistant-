import api from './api';
import { LoginRequest, RegisterRequest, AuthResponse, User } from '../types';

export class AuthService {
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const authData = response.data;

    // Store token and user data
    localStorage.setItem('access_token', authData.access_token);

    // Get user profile
    const userResponse = await api.get('/auth/me');
    const user = userResponse.data;
    localStorage.setItem('user', JSON.stringify(user));

    return {
      ...authData,
      user,
    };
  }

  static async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post('/auth/register', userData);

    // Auto-login after registration
    return this.login(userData);
  }

  static async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      return null;
    }
  }

  static logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  static isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  static getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
}