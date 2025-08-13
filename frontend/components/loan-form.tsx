"use client";

import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Badge } from "@/components/ui/badge";
import { apiClient, AssessRequest, AssessResponse } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import {
  Building2,
  TrendingUp,
  DollarSign,
  FileText,
  CheckCircle,
  XCircle,
} from "lucide-react";

interface FormData {
  businessName: string;
  industryType: string;
  annualTurnover: number;
  netProfit: number;
  loanAmount: number;
  udyamRegistration: boolean;
  district: string;
  state: string;
  businessPlan: string;
}

interface FormErrors {
  businessName?: string;
  industryType?: string;
  annualTurnover?: string;
  netProfit?: string;
  loanAmount?: string;
  district?: string;
  state?: string;
  businessPlan?: string;
}

const industryTypes = [
  { value: "manufacturing", label: "Manufacturing" },
  { value: "services", label: "Services" },
  { value: "trading", label: "Trading" },
  { value: "other", label: "Other" },
];

const indianStates = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
  "Andaman and Nicobar Islands",
  "Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi",
  "Jammu and Kashmir",
  "Ladakh",
  "Lakshadweep",
  "Puducherry",
];

const initialFormData: FormData = {
  businessName: "",
  industryType: "",
  annualTurnover: 1000000,
  netProfit: 200000,
  loanAmount: 500000,
  udyamRegistration: false,
  district: "",
  state: "",
  businessPlan: "",
};

export function LoanForm() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<AssessResponse | null>(null);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.businessName.trim()) {
      newErrors.businessName = "Business name is required";
    }

    if (!formData.industryType) {
      newErrors.industryType = "Industry type is required";
    }

    if (formData.annualTurnover < 100000) {
      newErrors.annualTurnover = "Annual turnover must be at least ₹1,00,000";
    }

    if (formData.netProfit < 0) {
      newErrors.netProfit = "Net profit cannot be negative";
    }

    if (formData.loanAmount < 100000) {
      newErrors.loanAmount = "Loan amount must be at least ₹1,00,000";
    }

    if (formData.loanAmount > formData.annualTurnover * 2) {
      newErrors.loanAmount =
        "Loan amount cannot exceed 200% of annual turnover";
    }

    if (!formData.district.trim()) {
      newErrors.district = "District is required";
    }

    if (!formData.state.trim()) {
      newErrors.state = "State is required";
    }

    if (!formData.businessPlan.trim()) {
      newErrors.businessPlan = "Business plan is required";
    } else if (formData.businessPlan.length < 100) {
      newErrors.businessPlan = "Business plan must be at least 100 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setResult(null);

    try {
      const response = await apiClient.assess(formData);
      setResult(response);
    } catch (error) {
      console.error("Assessment failed:", error);
      // Handle error - you might want to show a toast notification
    } finally {
      setIsSubmitting(false);
    }
  };

  const getScoreBadgeVariant = (score: number) => {
    if (score <= 3) return "red";
    if (score <= 6) return "amber";
    if (score <= 8) return "green";
    return "emerald";
  };

  const getScoreLabel = (score: number) => {
    if (score <= 3) return "High Risk";
    if (score <= 6) return "Medium Risk";
    if (score <= 8) return "Low Risk";
    return "Excellent";
  };

  return (
    <div className="space-y-8">
      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Business Information
          </CardTitle>
          <CardDescription>
            Fill in your business details for AI-powered loan assessment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Business Name */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Business Name *</label>
              <Input
                value={formData.businessName}
                onChange={(e) =>
                  setFormData({ ...formData, businessName: e.target.value })
                }
                placeholder="Enter your business name"
                error={!!errors.businessName}
              />
              {errors.businessName && (
                <p className="text-sm text-destructive">
                  {errors.businessName}
                </p>
              )}
            </div>

            {/* Industry Type */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Industry Type *</label>
              <Select
                value={formData.industryType}
                onChange={(e) =>
                  setFormData({ ...formData, industryType: e.target.value })
                }
                error={!!errors.industryType}
              >
                <option value="">Select industry type</option>
                {industryTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Select>
              {errors.industryType && (
                <p className="text-sm text-destructive">
                  {errors.industryType}
                </p>
              )}
            </div>

            {/* Financial Information */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Annual Turnover *
                </label>
                <Input
                  type="number"
                  value={formData.annualTurnover}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      annualTurnover: Number(e.target.value),
                    })
                  }
                  placeholder="Enter annual turnover"
                  error={!!errors.annualTurnover}
                />
                <p className="text-xs text-muted-foreground">
                  Min: ₹1,00,000 | Max: ₹1,00,00,000
                </p>
                {errors.annualTurnover && (
                  <p className="text-sm text-destructive">
                    {errors.annualTurnover}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  Net Profit *
                </label>
                <Input
                  type="number"
                  value={formData.netProfit}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      netProfit: Number(e.target.value),
                    })
                  }
                  placeholder="Enter net profit"
                  error={!!errors.netProfit}
                />
                <p className="text-xs text-muted-foreground">
                  Cannot exceed annual turnover
                </p>
                {errors.netProfit && (
                  <p className="text-sm text-destructive">{errors.netProfit}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Loan Amount Required *
                </label>
                <Input
                  type="number"
                  value={formData.loanAmount}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      loanAmount: Number(e.target.value),
                    })
                  }
                  placeholder="Enter loan amount"
                  error={!!errors.loanAmount}
                />
                <p className="text-xs text-muted-foreground">
                  Min: ₹1,00,000 | Max: 200% of turnover
                </p>
                {errors.loanAmount && (
                  <p className="text-sm text-destructive">
                    {errors.loanAmount}
                  </p>
                )}
              </div>
            </div>

            {/* Udyam Registration and Location */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Udyam Registration
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="udyamRegistration"
                      checked={formData.udyamRegistration === true}
                      onChange={() =>
                        setFormData({ ...formData, udyamRegistration: true })
                      }
                      className="sr-only"
                    />
                    <div
                      className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        formData.udyamRegistration === true
                          ? "border-primary bg-primary"
                          : "border-muted-foreground"
                      }`}
                    >
                      {formData.udyamRegistration === true && (
                        <CheckCircle className="w-3 h-3 text-primary-foreground" />
                      )}
                    </div>
                    <span className="text-sm">Yes</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="udyamRegistration"
                      checked={formData.udyamRegistration === false}
                      onChange={() =>
                        setFormData({ ...formData, udyamRegistration: false })
                      }
                      className="sr-only"
                    />
                    <div
                      className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        formData.udyamRegistration === false
                          ? "border-primary bg-primary"
                          : "border-muted-foreground"
                      }`}
                    >
                      {formData.udyamRegistration === false && (
                        <XCircle className="w-3 h-3 text-primary-foreground" />
                      )}
                    </div>
                    <span className="text-sm">No</span>
                  </label>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">District *</label>
                <Input
                  value={formData.district}
                  onChange={(e) =>
                    setFormData({ ...formData, district: e.target.value })
                  }
                  placeholder="Enter district"
                  error={!!errors.district}
                />
                {errors.district && (
                  <p className="text-sm text-destructive">{errors.district}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">State *</label>
                <Select
                  value={formData.state}
                  onChange={(e) =>
                    setFormData({ ...formData, state: e.target.value })
                  }
                  error={!!errors.state}
                >
                  <option value="">Select state</option>
                  {indianStates.map((state) => (
                    <option key={state} value={state}>
                      {state}
                    </option>
                  ))}
                </Select>
                {errors.state && (
                  <p className="text-sm text-destructive">{errors.state}</p>
                )}
              </div>
            </div>

            {/* Business Plan */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Business Plan *</label>
              <Textarea
                value={formData.businessPlan}
                onChange={(e) =>
                  setFormData({ ...formData, businessPlan: e.target.value })
                }
                placeholder="Describe your business plan including use of funds, revenue projections, and repayment strategy..."
                rows={6}
                error={!!errors.businessPlan}
              />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Minimum 100 characters</span>
                <span>{formData.businessPlan.length}/2000</span>
              </div>
              {errors.businessPlan && (
                <p className="text-sm text-destructive">
                  {errors.businessPlan}
                </p>
              )}
            </div>

            {/* Submit and Clear Buttons */}
            <div className="flex gap-4">
              <Button type="submit" className="flex-1" loading={isSubmitting}>
                {isSubmitting ? "Assessing..." : "Assess Loan Application"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setFormData(initialFormData);
                  setErrors({});
                  setResult(null);
                }}
              >
                Clear Form
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              Assessment Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Score Display */}
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div>
                <h3 className="text-lg font-semibold">Loan Score</h3>
                <p className="text-sm text-muted-foreground">
                  Based on your business profile and LightRAG analysis
                </p>
              </div>
              <div className="text-right">
                <Badge
                  variant={getScoreBadgeVariant(result.score)}
                  className="text-lg px-4 py-2"
                >
                  {result.score}/10
                </Badge>
                <p className="text-sm text-muted-foreground mt-1">
                  {getScoreLabel(result.score)}
                </p>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="space-y-3">
              <h4 className="font-semibold">Score Breakdown</h4>
              <div className="space-y-2">
                {result.details.breakdown.map((item, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center p-2 bg-muted/50 rounded"
                  >
                    <span className="text-sm">{item.reason}</span>
                    <Badge
                      variant={item.points >= 0 ? "secondary" : "destructive"}
                    >
                      {item.points >= 0 ? "+" : ""}
                      {item.points}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div className="space-y-3">
              <h4 className="font-semibold">AI-Powered Recommendations</h4>
              <div className="space-y-3">
                {result.recommendations.map((recommendation, index) => (
                  <div
                    key={index}
                    className="p-6 bg-muted/30 rounded-lg border-l-4 border-primary"
                  >
                    <div className="max-h-96 overflow-y-auto">
                      <p className="text-base leading-relaxed whitespace-pre-wrap">
                        {recommendation.length > 1000
                          ? recommendation.substring(0, 1000) +
                            "... (truncated)"
                          : recommendation}
                      </p>
                    </div>
                    {recommendation.length > 1000 && (
                      <p className="text-xs text-muted-foreground mt-2">
                        Recommendation truncated to 1000 words for display
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Financial Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-muted rounded-lg">
              <div>
                <p className="text-sm text-muted-foreground">Profit Margin</p>
                <p className="text-lg font-semibold">
                  {result.details.derived.profit_margin_pct.toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">
                  Loan-to-Turnover Ratio
                </p>
                <p className="text-lg font-semibold">
                  {result.details.derived.loan_to_turnover_pct.toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
