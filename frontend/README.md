# MSME Loan Scorer Frontend

A modern, dark-themed Next.js frontend for the MSME Loan Scorer application with LightRAG integration.

## Features

- 🎨 **Dark Theme**: Beautiful dark UI with Tailwind CSS
- 📝 **Form Validation**: Inline validation with real-time feedback
- 🎯 **Interactive Sliders**: Smooth amount sliders with currency formatting
- 📊 **Score Display**: Color-coded score badges (red, amber, green, emerald)
- 🤖 **AI Recommendations**: LightRAG-powered recommendations from PDF documents
- 📱 **Responsive Design**: Works perfectly on desktop and mobile
- ⚡ **Real-time Updates**: Live character count and validation

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client for API calls

## Getting Started

### Prerequisites

- Node.js 18+ 
- Backend server running on `http://localhost:8000`

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Form Fields

The application includes all required fields:

- **Business Name** (text input)
- **Industry Type** (select: Manufacturing, Services, Trading, Other)
- **Annual Turnover** (slider: ₹1L - ₹1Cr)
- **Net Profit** (slider: ₹0 - Annual Turnover)
- **Loan Amount Required** (slider: ₹1L - 200% of Annual Turnover)
- **Udyam Registration** (Yes/No radio buttons)
- **Business Plan** (textarea with character count)

## Validation Rules

- Business name: Required
- Industry type: Required
- Annual turnover: Minimum ₹1,00,000
- Net profit: Cannot be negative
- Loan amount: Between ₹1,00,000 and 200% of annual turnover
- Business plan: Minimum 100 characters, maximum 2000

## Score Display

The application shows:

- **Color-coded score badge**:
  - 0-3: Red (High Risk)
  - 4-6: Amber (Medium Risk)
  - 7-8: Green (Low Risk)
  - 9-10: Emerald (Excellent)

- **Score breakdown** with individual scoring factors
- **AI-powered recommendations** from LightRAG analysis
- **Financial summary** with profit margin and loan-to-turnover ratio

## API Integration

The frontend communicates with the backend API:

- `POST /api/assess` - Submit loan application
- `POST /api/search` - Search documents
- `POST /api/generate` - Generate answers
- `GET /api/health` - Health check
- `GET /api/documents` - Get document info

## Development

### Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   └── loan-form.tsx     # Main loan form
├── lib/                  # Utilities
│   ├── api.ts           # API client
│   └── utils.ts         # Helper functions
└── package.json         # Dependencies
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

The frontend can be deployed to Vercel, Netlify, or any other hosting platform that supports Next.js.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
