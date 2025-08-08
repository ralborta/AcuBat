'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { 
  Phone, 
  Clock, 
  TrendingUp, 
  AlertTriangle, 
  Users, 
  Activity,
  Eye,
  Download
} from 'lucide-react'
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'

// Datos de ejemplo para las métricas
const metricsData = [
  {
    title: "Total de Productos",
    value: "1,247",
    change: "+12%",
    status: "Mejorando",
    icon: Phone,
    progress: 85,
    color: "bg-blue-500"
  },
  {
    title: "Margen Promedio",
    value: "35.2%",
    change: "+5%",
    status: "Mejorando",
    icon: Clock,
    progress: 78,
    color: "bg-green-500"
  },
  {
    title: "Tasa de Éxito",
    value: "87%",
    change: "+8%",
    status: "Mejorando",
    icon: TrendingUp,
    progress: 87,
    color: "bg-purple-500"
  },
  {
    title: "Productos Críticos",
    value: "89",
    change: "-3%",
    status: "Necesita atención",
    icon: AlertTriangle,
    progress: 45,
    color: "bg-yellow-500"
  },
  {
    title: "Simulaciones",
    value: "23",
    change: "-15%",
    status: "Mejorando",
    icon: Users,
    progress: 92,
    color: "bg-pink-500"
  },
  {
    title: "Tiempo Total",
    value: "94h 12m",
    change: "+7%",
    status: "Mejorando",
    icon: Activity,
    progress: 73,
    color: "bg-indigo-500"
  }
]

// Datos para el gráfico de productos por día
const productsByDayData = [
  { date: '02/08', productos: 45 },
  { date: '03/08', productos: 52 },
  { date: '04/08', productos: 38 },
  { date: '05/08', productos: 58 },
  { date: '06/08', productos: 42 },
  { date: '07/08', productos: 49 },
  { date: '08/08', productos: 55 }
]

// Datos para el gráfico de distribución de márgenes
const marginDistributionData = [
  { name: 'Óptimo (≥20%)', value: 65, color: '#10B981' },
  { name: 'Advertencia (10-20%)', value: 25, color: '#F59E0B' },
  { name: 'Crítico (<10%)', value: 10, color: '#EF4444' }
]

// Datos para el gráfico de barras de marcas
const brandsData = [
  { marca: 'Moura', productos: 47, margen: 35.2 },
  { marca: 'Varta', productos: 32, margen: 28.5 },
  { marca: 'Willard', productos: 25, margen: 31.8 },
  { marca: 'AcuBat', productos: 18, margen: 29.4 }
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Resumen de actividad de la plataforma de pricing</p>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-500">
            {new Date().toLocaleDateString('es-ES', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </span>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700">
            <Activity className="w-4 h-4" />
            <span>Actualizar</span>
          </button>
        </div>
      </div>

      {/* Métricas Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metricsData.map((metric, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {metric.title}
              </CardTitle>
              <metric.icon className={`h-4 w-4 ${metric.color.replace('bg-', 'text-')}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
              <div className="flex items-center space-x-2 mt-2">
                <span className={`text-sm ${
                  metric.change.startsWith('+') ? 'text-green-600' : 'text-red-600'
                }`}>
                  {metric.change}
                </span>
                <span className="text-sm text-gray-500">{metric.status}</span>
              </div>
              <Progress value={metric.progress} className="mt-4" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Productos por Día */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Productos por Día</CardTitle>
                <p className="text-sm text-gray-600">Últimos 7 días de actividad</p>
              </div>
              <div className="flex space-x-2">
                <button className="p-2 hover:bg-gray-100 rounded">
                  <Eye className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={productsByDayData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="productos" 
                  stroke="#3B82F6" 
                  fill="#3B82F6" 
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Distribución de Márgenes */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Distribución de Márgenes</CardTitle>
                <p className="text-sm text-gray-600">Estado de rentabilidad por producto</p>
              </div>
              <div className="flex space-x-2">
                <button className="p-2 hover:bg-gray-100 rounded">
                  <Eye className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-6">
              <ResponsiveContainer width="60%" height={300}>
                <PieChart>
                  <Pie
                    data={marginDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {marginDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-3">
                {marginDistributionData.map((item, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm text-gray-600">{item.name}</span>
                    <span className="text-sm font-medium">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráfico de Marcas */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Productos por Marca</CardTitle>
              <p className="text-sm text-gray-600">Distribución y márgenes por marca</p>
            </div>
            <div className="flex space-x-2">
              <button className="p-2 hover:bg-gray-100 rounded">
                <Eye className="w-4 h-4" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded">
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={brandsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="marca" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Bar yAxisId="left" dataKey="productos" fill="#3B82F6" />
              <Bar yAxisId="right" dataKey="margen" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
