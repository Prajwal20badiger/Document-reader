const API_BASE_URL = 'http://localhost:8000';

export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`Health check returned status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.warn('Backend health check error:', error);
    return {
      status: 'offline',
      ocr_available: false,
      ai_configured: false,
      max_upload_size_mb: 15,
      allowed_extensions: ['.pdf', '.txt', '.png', '.jpg', '.jpeg']
    };
  }
}

export async function analyzeDocument(file, customKey = '', customModel = '') {
  const formData = new FormData();
  formData.append('file', file);

  const headers = {};
  if (customKey && customKey.trim()) {
    headers['x-ai-api-key'] = customKey.trim();
  }
  if (customModel && customModel.trim()) {
    headers['x-ai-model'] = customModel.trim();
  }

  const response = await fetch(`${API_BASE_URL}/api/documents/analyze`, {
    method: 'POST',
    headers,
    body: formData,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const err = data.error || {
      code: `HTTP_${response.status}`,
      message: 'Failed to process document.',
      suggestion: 'Please try again or check your file format.'
    };
    const errorObj = new Error(err.message);
    errorObj.code = err.code;
    errorObj.suggestion = err.suggestion;
    throw errorObj;
  }

  return data;
}
