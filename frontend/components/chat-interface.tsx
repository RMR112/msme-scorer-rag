"use client";

import React, { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { Send, Bot, User, FileText } from "lucide-react";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  citations?: Citation[];
}

interface Citation {
  document_name: string;
  page_number?: number;
  content: string;
  score: number;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content:
        "Hello! I'm your MSME loan advisor. I can help you with questions about MSME loans, eligibility criteria, and application processes. Here are some things you can ask me:\n\n• What are the eligibility criteria for MSME loans?\n• What documents are required for loan application?\n• What is the maximum loan amount available?\n• How does the loan approval process work?\n• What are the interest rates and repayment terms?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const searchResponse = await apiClient.search({
        query: inputValue,
        top_k: 3,
      });

      const generateResponse = await apiClient.generate({
        query: inputValue,
      });

      const citations: Citation[] = searchResponse.results.map(
        (result, index) => {
          // Extract document name from metadata with fallbacks
          let docName = "MSME Policy Document";

          // Try multiple sources for document name
          if (result.document_metadata?.document_name) {
            docName = result.document_metadata.document_name;
          } else if (result.document_metadata?.source_file) {
            docName = result.document_metadata.source_file;
          } else if (result.document_metadata?.document_id) {
            docName = result.document_metadata.document_id;
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
        }
      );

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: generateResponse.answer,
        sender: "bot",
        timestamp: new Date(),
        citations: citations.length > 0 ? citations : undefined,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error: any) {
      console.error("Chat error:", error);

      let errorContent =
        "I apologize, but I'm having trouble accessing the information right now. Please try again in a moment.";

      // Handle validation errors
      if (
        error.response?.status === 400 &&
        error.response?.data?.error === "Query validation failed"
      ) {
        const validationData = error.response.data;
        errorContent = `${
          validationData.reason
        }\n\nHere are some suggested questions you can ask:\n\n${validationData.suggested_questions
          ?.map((q: string, i: number) => `${i + 1}. ${q}`)
          .join("\n")}`;
      }

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: errorContent,
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-background">
      <CardHeader className="border-b bg-muted/30">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Bot className="h-5 w-5 text-primary" />
          MSME Loan Advisor
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Ask questions about loan requirements, eligibility, and policies
        </p>
      </CardHeader>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {message.sender === "bot" && (
              <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
            )}

            <div
              className={`max-w-[80%] space-y-2 ${
                message.sender === "user"
                  ? "bg-primary text-primary-foreground rounded-lg rounded-br-none px-4 py-2"
                  : "bg-muted rounded-lg rounded-bl-none px-4 py-2"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>

              {message.citations && message.citations.length > 0 && (
                <div className="space-y-2 mt-3 pt-3 border-t border-border/50">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <FileText className="h-3 w-3" />
                    <span>Sources:</span>
                  </div>
                  {message.citations.map((citation, index) => (
                    <div
                      key={index}
                      className="bg-background/50 rounded p-2 text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-foreground">
                          {citation.document_name}
                        </span>
                        <Badge variant="secondary" className="text-xs">
                          {citation.score.toFixed(2)}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <FileText className="h-3 w-3" />
                        <span>Source {index + 1}</span>
                        {citation.page_number && (
                          <>
                            <span>•</span>
                            <span>Page {citation.page_number}</span>
                          </>
                        )}
                      </div>
                      <p className="text-muted-foreground italic text-xs leading-relaxed">
                        "{citation.content}"
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {message.sender === "user" && (
              <div className="flex-shrink-0 w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-muted-foreground" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="bg-muted rounded-lg rounded-bl-none px-4 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t bg-muted/30 p-4">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about MSME loans, eligibility, or policies..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
