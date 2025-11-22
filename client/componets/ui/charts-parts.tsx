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

const ChartTooltip: React.FC<any> = ({ active, payload }) => {
  if (active && payload && payload.length) {
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