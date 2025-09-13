/**
 * Mock API client for testing
 */

/**
 * Create an API client
 * @param {Object} options - API client options
 * @param {string} options.baseUrl - Base URL for API requests
 * @param {number} options.timeout - Request timeout in milliseconds
 * @returns {Object} - API client
 */
function createApiClient(options = {}) {
  const baseUrl = options.baseUrl || 'http://localhost:8000';
  const timeout = options.timeout || 5000;
  
  return {
    /**
     * Send a GET request
     * @param {string} path - Request path
     * @param {Object} options - Request options
     * @returns {Promise<Object>} - Response
     */
    get: async (path, options = {}) => {
      // Mock implementation for testing
      if (path === '/error') {
        const error = new Error('Internal server error');
        error.response = {
          status: 500,
          data: { error: 'Internal server error' }
        };
        throw error;
      }
      
      return {
        status: 200,
        data: { message: 'Test successful' }
      };
    },
    
    /**
     * Send a POST request
     * @param {string} path - Request path
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise<Object>} - Response
     */
    post: async (path, data, options = {}) => {
      // Mock implementation for testing
      return {
        status: 200,
        data: { message: 'Test successful' }
      };
    },
    
    /**
     * Send a PUT request
     * @param {string} path - Request path
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise<Object>} - Response
     */
    put: async (path, data, options = {}) => {
      // Mock implementation for testing
      return {
        status: 200,
        data: { message: 'Test successful' }
      };
    },
    
    /**
     * Send a DELETE request
     * @param {string} path - Request path
     * @param {Object} options - Request options
     * @returns {Promise<Object>} - Response
     */
    delete: async (path, options = {}) => {
      // Mock implementation for testing
      return {
        status: 200,
        data: { message: 'Test successful' }
      };
    }
  };
}

module.exports = {
  createApiClient
};
