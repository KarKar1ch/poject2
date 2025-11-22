"use client"

import * as React from "react"
import { PieChart, Pie, Tooltip, ResponsiveContainer, Label, Cell } from "recharts"

interface ChartConfig {
  [key: string]: {
    label: string
    color: string
  }
}

interface ChartContainerProps {
  config: ChartConfig
  children: React.ReactNode
  className?: string
  style?: React.CSSProperties
}

const ChartContainer: React.FC<ChartContainerProps> = ({ 
  config, 
  children, 
  className,
  style 
}) => {
  return (
    <div className={className} style={style}>
      <ResponsiveContainer width="100%" height="100%">
        {children}
      </ResponsiveContainer>
    </div>
  )
}

const ChartTooltip: React.FC<any> = ({ active, payload, label, formatter }) => {
  if (active && payload && payload.length) {
    // Если передан кастомный formatter
    if (formatter) {
      const [formattedValue, formattedName] = formatter(payload[0].value, payload[0].name, payload[0], 0, payload);
      if (formattedValue === null) return null; // Скрываем тултип для background
      
      return (
        <div className="bg-background border rounded-lg shadow-lg p-3">
          <p className="font-medium">{formattedName || payload[0].name}</p>
          <p className="text-muted-foreground">{formattedValue || payload[0].value.toLocaleString()}</p>
        </div>
      )
    }
    
    // Стандартный тултип
    return (
      <div className="bg-background border rounded-lg shadow-lg p-3">
        <p className="font-medium">{payload[0].name}</p>
        <p className="text-muted-foreground">{payload[0].value.toLocaleString()}</p>
      </div>
    )
  }
  return null
}

export {
  ChartContainer,
  ChartTooltip,
  PieChart,
  Pie,
  Label,
  Cell
}