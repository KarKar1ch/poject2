import * as React from "react"

interface ChartConfig {
  [key: string]: {
    label: string;
    color?: string;
  }
}

interface ChartContainerProps {
  config: ChartConfig;
  className?: string;
  children: React.ReactNode;
}

export const ChartContainer: React.FC<ChartContainerProps> = ({ 
  config, 
  className, 
  children 
}) => {
  return <div className={className}>{children}</div>
}

export type { ChartConfig }