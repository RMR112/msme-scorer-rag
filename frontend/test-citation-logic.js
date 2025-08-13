// Test the citation logic that's used in the chat interface
function testCitationLogic() {
  // Simulate the API response structure
  const mockSearchResponse = {
    results: [
      {
        rank: 1,
        content:
          "### Eligibility Criteria for MSME Loans\n\nMicro, Small, and Medium Enterprises (MSME) loans are designed to provide financial assistance to small businesses...",
        score: 1.0,
        metadata: {},
        document_metadata: {
          document_id: "msme_loan",
          document_name: "MSME Loan.pdf",
          document_type: "MSME_POLICY_DOCUMENT",
          source_file: "MSME Loan.pdf",
        },
      },
    ],
    total_results: 1,
  };

  // Simulate the citation mapping logic from chat-interface.tsx
  const citations = mockSearchResponse.results.map((result, index) => {
    // Extract document name from metadata with fallbacks
    let docName = "MSME Policy Document";

    // Try multiple sources for document name
    if (result.document_metadata?.document_name) {
      docName = result.document_metadata.document_name;
      console.log(`Found document name: ${docName}`);
    } else if (result.document_metadata?.source_file) {
      docName = result.document_metadata.source_file;
      console.log(`Using source file: ${docName}`);
    } else if (result.document_metadata?.document_id) {
      docName = result.document_metadata.document_id;
      console.log(`Using document ID: ${docName}`);
    } else {
      console.log(`No document name found for result ${index + 1}`);
    }

    // Clean up the filename for display
    if (docName.endsWith(".pdf")) {
      docName = docName.replace(".pdf", "");
    }
    // Replace underscores with spaces and make it more readable
    docName = docName.replace(/_/g, " ").replace(/\d{8}/, "").trim();

    // Handle specific document names for better display
    if (docName.toLowerCase().includes("sme intensive branches")) {
      docName = "SME Intensive Branches";
    } else if (docName.toLowerCase().includes("msme loan")) {
      docName = "MSME Loan Guidelines";
    } else if (
      docName.toLowerCase().includes("msme_e-book") ||
      docName.toLowerCase().includes("e-book")
    ) {
      docName = "MSME E-Book of Schemes";
    }

    return {
      document_name: docName,
      page_number: result.document_metadata?.page_number,
      content: result.content.substring(0, 200) + "...",
      score: result.score || 0,
    };
  });

  console.log("Final citations:", citations);
  return citations;
}

// Run the test
const citations = testCitationLogic();
console.log("Test completed. Citations:", citations);
