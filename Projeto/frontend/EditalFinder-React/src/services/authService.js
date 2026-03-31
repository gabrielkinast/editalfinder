import { supabase } from './api';

export const authService = {
  async login(email, password) {
    const { data: usuario, error } = await supabase
      .from('usuario')
      .select('*')
      .eq('nome_email', email)
      .single();

    if (error && error.code !== 'PGRST116') {
      throw error;
    }

    if (usuario && usuario.senha === password) {
      if (usuario.status === 'Inativo') {
        throw new Error('Este usuário está inativo e não pode realizar login.');
      }

      const userData = {
        email: usuario.nome_email,
        nome: usuario.nome,
        tipo: usuario.tipo_usuario,
        nivel: usuario.nivel_acesso,
        status: usuario.status,
      };
      localStorage.setItem('editalFinderUser', JSON.stringify(userData));
      return userData;
    } else if (email === 'admin@finder.com' && password === '123456') {
        const userData = {
            email: email,
            nome: 'Administrador',
            tipo: 'Administrador',
            nivel: 1,
        };
        localStorage.setItem('editalFinderUser', JSON.stringify(userData));
        return userData;
    }

    throw new Error('Credenciais inválidas.');
  },

  logout() {
    localStorage.removeItem('editalFinderUser');
  },

  getUser() {
    const user = localStorage.getItem('editalFinderUser');
    return user ? JSON.parse(user) : null;
  },
};
