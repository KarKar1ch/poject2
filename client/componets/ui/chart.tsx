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

// Tooltip компоненты
interface ChartTooltipProps {
  cursor?: boolean | { stroke: string; strokeWidth: number };
  content?: React.ReactElement;
}

export const ChartTooltip: React.FC<ChartTooltipProps> = ({ 
  cursor = false, 
  content 
}) => {
  return null
}

interface ChartTooltipContentProps {
  hideLabel?: boolean;
  className?: string;
  label?: string;
  payload?: any[];
  indicator?: string; // Добавляем пропс indicator
  [key: string]: any; // Добавляем индексную сигнатуру для любых других пропсов
}

export const ChartTooltipContent: React.FC<ChartTooltipContentProps> = ({ 
  hideLabel = false,
  className = "",
  label,
  payload,
  indicator, // Добавляем indicator в деструктуризацию
  ...rest // Остальные пропсы
}) => {
  if (!payload || payload.length === 0) return null

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-lg p-3 ${className}`}>
      {!hideLabel && label && (
        <div className="font-medium text-gray-900 mb-2">{label}</div>
      )}
      <div className="space-y-1">
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color || '#3b82f6' }}
            />
            <span className="text-gray-600">{entry.dataKey}:</span>
            <span className="font-medium text-gray-900">{entry.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export type { ChartConfig }