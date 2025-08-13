// Simple test to check API response in frontend
const testApiResponse = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: "What are the eligibility criteria for MSME loans?",
        top_k: 3,
        enable_rerank: false
      })
    });

    const data = await response.json();
    console.log('API Response:', JSON.stringify(data, null, 2));
    
    // Check each result
    data.results.forEach((result, index) => {
      console.log(`\nResult ${index + 1}:`);
      console.log('  Content preview:', result.content?.substring(0, 100));
      console.log('  Score:', result.score);
      console.log('  Document metadata keys:', Object.keys(result.document_metadata || {}));
      console.log('  Document name:', result.document_metadata?.document_name);
      console.log('  Document ID:', result.document_metadata?.document_id);
      console.log('  Source file:', result.document_metadata?.source_file);
    });
    
  } catch (error) {
    console.error('Error:', error);
  }
};

// Run the test
testApiResponse();
