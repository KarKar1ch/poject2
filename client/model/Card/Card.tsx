"use client"
import { TrendingUp } from "lucide-react"
import { RadialBar, RadialBarChart, PolarGrid, PolarRadiusAxis, Label } from "recharts"

// Простые компоненты карточек
const Card = ({ children, className }: any) => (
  <div className={`rounded-lg bg-white shadow-sm ${className}`}>
    {children}
  </div>
)

const CardHeader = ({ children, className }: any) => (
  <div className={`p-6 pb-0 ${className}`}>{children}</div>
)

const CardTitle = ({ children }: any) => (
  <h3 className="text-2xl font-semibold">{children}</h3>
)

const CardDescription = ({ children }: any) => (
  <p className="text-sm text-gray-500 mt-2">{children}</p>
)

const CardContent = ({ children, className }: any) => (
  <div className={`p-6 ${className}`}>{children}</div>
)

const CardFooter = ({ children, className }: any) => (
  <div className={`p-6 pt-0 ${className}`}>{children}</div>
)

const chartData = [
  { browser: "safari", visitors: 120, fill: "#3b82f6" },
]

export function ChartRadialText() {
  return (
    <Card className="flex flex-col">
      <CardHeader className="items-center pb-0">
        <CardTitle>Колличество компаний</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 pb-0">
        <div className="mx-auto aspect-square max-h-[250px]">
          <RadialBarChart
            width={280}
            height={280}
            data={chartData}
            startAngle={0}
            endAngle={250}
            innerRadius={100}
            outerRadius={120}
          >
            <PolarGrid
              gridType="circle"
              radialLines={true}
              stroke="none"
            />
            <RadialBar 
              dataKey="visitors" 
              background 
              cornerRadius={50}
              fill="#3b82f6"
            />
            <PolarRadiusAxis tick={false} tickLine={false} axisLine={false}>
              <Label
                content={({ viewBox }: any) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="fill-foreground text-4xl font-bold"
                        >
                          {chartData[0].visitors.toLocaleString()}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="fill-muted-foreground"
                        >
                          Всего
                        </tspan>
                      </text>
                    )
                  }
                }}
              />
            </PolarRadiusAxis>
          </RadialBarChart>
        </div>
      </CardContent>
      <CardFooter className="flex-col gap-2 text-sm">
        <div className="flex items-center gap-2 leading-none font-medium">
          Выросло 5.2% за ноябрь <TrendingUp className="h-4 w-4 mt-[10px]" />
        </div>
      </CardFooter>
    </Card>
  )
}