"use client";

import React from "react";

// Card компоненты
export const ChartCard = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={`bg-white w-full ${className}`}>
    {children}
  </div>
);

export const ChartCardHeader = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={` ${className}`}>
    {children}
  </div>
);

export const ChartCardTitle = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <h3 className={`text-lg font-semibold leading-none tracking-tight ${className}`}>
    {children}
  </h3>
);

export const ChartCardDescription = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <p className={`text-sm text-gray-600 mt-2 ${className}`}>
    {children}
  </p>
);

export const ChartCardContent = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={` pt-0 ${className}`}>
    {children}
  </div>
);

export const ChartCardFooter = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={` ${className}`}>
    {children}
  </div>
);

// Chart компоненты
export interface ChartConfig {
  [key: string]: {
    label: string;
    color: string;
  };
}

export const ChartContainer = ({ 
  children, 
  config,
  className 
}: { 
  children: React.ReactNode; 
  config: ChartConfig;
  className?: string;
}) => (
  <div className={className}>
    {children}
  </div>
);

export const ChartTooltip = ({ 
  children,
  cursor,
  content
}: { 
  children?: React.ReactNode;
  cursor?: boolean;
  content?: React.ReactNode;
}) => (
  <>{children}</>
);

export const ChartTooltipContent = ({ 
  indicator 
}: { 
  indicator?: string;
}) => (
  <div></div>
);