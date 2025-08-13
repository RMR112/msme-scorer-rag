"use client";

import React, { useState } from "react";
import { LoanForm } from "@/components/loan-form";
import { ChatInterface } from "@/components/chat-interface";
import { Button } from "@/components/ui/button";
import { MessageSquare, X } from "lucide-react";

export function MainLayout() {
  const [isChatOpen, setIsChatOpen] = useState(true);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="text-center flex-1">
              <h1 className="text-2xl font-bold text-foreground">
                MSME Loan Scorer
              </h1>
              <p className="text-sm text-muted-foreground">
                AI-powered loan assessment with LightRAG document analysis
              </p>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setIsChatOpen(!isChatOpen)}
              className="lg:hidden"
            >
              {isChatOpen ? <X className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content Area */}
          <div className={`${isChatOpen ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
            <LoanForm />
          </div>

          {/* Chat Sidebar */}
          {isChatOpen && (
            <div className="lg:col-span-1">
              <div className="sticky top-8 h-[calc(100vh-8rem)]">
                <ChatInterface />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Chat Toggle */}
      {!isChatOpen && (
        <div className="fixed bottom-6 right-6 lg:hidden">
          <Button
            size="icon"
            className="h-12 w-12 rounded-full shadow-lg"
            onClick={() => setIsChatOpen(true)}
          >
            <MessageSquare className="h-5 w-5" />
          </Button>
        </div>
      )}
    </div>
  );
}
