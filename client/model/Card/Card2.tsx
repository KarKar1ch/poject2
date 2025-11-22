"use client"
import { TrendingUp } from "lucide-react"
import { RadialBar, RadialBarChart, PolarRadiusAxis, Label } from "recharts"

// --- Компоненты карточек ---
const Card = ({ children, className }: any) => (
  <div className={`rounded-[30px] bg-white shadow-sm border border-slate-100 w-[350px] ${className}`}>
    {children}
  </div>
)

const CardHeader = ({ children, className }: any) => (
  <div className={`p-6 pb-0 flex flex-col items-start ${className}`}>{children}</div>
)

const CardTitle = ({ children }: any) => (
  <h3 className="text-lg font-bold text-slate-900">{children}</h3>
)

const CardDescription = ({ children }: any) => (
  <p className="text-sm font-medium text-slate-400 mt-1">{children}</p>
)

const CardContent = ({ children, className }: any) => (
  <div className={`p-6 ${className}`}>{children}</div>
)

const CardFooter = ({ children, className }: any) => (
  <div className={`p-6 pt-0 flex justify-center ${className}`}>{children}</div>
)

export function ChartRadialText2() {
  const total = 274;
  const filledPercentage = 75; // Процент заполнения
  
  // Данные для графика - сначала фон (полный круг), потом основная часть
  const chartData = [
    { 
      name: "background", 
      value: 100, // Полный круг - 100%
      fill: "#ECEDF0" // Серый цвет для фона
    },
    { 
      name: "main", 
      value: filledPercentage, // Процент заполнения
      fill: "#5D39F5" // Фиолетовый цвет
    },
  ]

  return (
    <Card className="flex flex-col">
      <CardHeader>
        <CardTitle>Компании без задолженностей</CardTitle>
        <CardDescription>Ноябрь</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 pb-0">
        <div className="mx-auto aspect-square max-h-[250px] flex justify-center">
          <RadialBarChart
            width={250}
            height={250}
            data={chartData}
            innerRadius={90}
            outerRadius={120}
            startAngle={0}
            endAngle={360}
          >
            {/* RadialBar для отображения всех данных */}
            <RadialBar 
              dataKey="value"
              cornerRadius={20}
              // Убираем background, так как создаем фон через данные
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
                          className="fill-slate-900 text-5xl font-bold"
                        >
                          {total}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 30}
                          className="fill-slate-400 text-lg font-medium"
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
        <div className="flex items-center gap-2 leading-none font-bold text-slate-900 text-base">
          <TrendingUp className="h-4 w-4" />
          Выросло на 1.53%
        </div>
      </CardFooter>
    </Card>
  )
}