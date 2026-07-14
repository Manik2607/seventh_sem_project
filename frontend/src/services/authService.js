export const authService = {
  login: (email, password) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          user: { id: '1', name: 'John Doe', email },
          token: 'mock-jwt-token-12345',
          role: 'Citizen', // Default mock role
        });
      }, 1000);
    });
  },
  logout: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 1000);
    });
  },
};

export default authService;
