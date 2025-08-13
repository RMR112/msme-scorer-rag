import * as React from "react";
import { cn } from "@/lib/utils";

export interface SliderProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  value?: number;
  min?: number;
  max?: number;
  step?: number;
  formatValue?: (value: number) => string;
  error?: boolean;
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ className, label, value, min = 0, max = 1000000, step = 10000, formatValue, error, ...props }, ref) => {
    const [displayValue, setDisplayValue] = React.useState(value || min);
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = Number(e.target.value);
      setDisplayValue(newValue);
      if (props.onChange) {
        props.onChange(e);
      }
    };

    const formatDisplayValue = formatValue || ((val: number) => 
      new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(val)
    );

    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            {label}
          </label>
        )}
        <div className="space-y-4">
          <input
            type="range"
            ref={ref}
            min={min}
            max={max}
            step={step}
            value={displayValue}
            onChange={handleChange}
            className={cn(
              "w-full",
              error && "border-destructive focus-visible:ring-destructive",
              className
            )}
            {...props}
          />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>{formatDisplayValue(min)}</span>
            <span className="font-medium text-foreground">
              {formatDisplayValue(displayValue)}
            </span>
            <span>{formatDisplayValue(max)}</span>
          </div>
        </div>
      </div>
    );
  }
);
Slider.displayName = "Slider";

export { Slider };
