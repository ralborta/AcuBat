'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Grid3X3, 
  Phone, 
  MessageSquare, 
  Upload, 
  Settings, 
  BarChart3, 
  HelpCircle,
  Bell,
  Search,
  ChevronDown
} from 'lucide-react'

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Grid3X3,
    description: 'Vista general del call center'
  },
  {
    name: 'Carga de Archivos',
    href: '/upload',
    icon: Upload,
    description: 'Subir archivos Excel'
  },
  {
    name: 'Simulaciones',
    href: '/simulate',
    icon: Phone,
    description: 'Ejecutar simulaciones de pricing'
  },
  {
    name: 'Rulesets',
    href: '/rulesets',
    icon: MessageSquare,
    description: 'Gestionar reglas de pricing'
  },
  {
    name: 'Publicaciones',
    href: '/publish',
    icon: BarChart3,
    description: 'Publicar resultados'
  },
  {
    name: 'Configuración',
    href: '/settings',
    icon: Settings,
    description: 'Configurar sistema'
  },
  {
    name: 'Reportes',
    href: '/reports',
    icon: BarChart3,
    description: 'Generar reportes'
  },
  {
    name: 'Ayuda',
    href: '/help',
    icon: HelpCircle,
    description: 'Centro de ayuda'
  }
]

export function Sidebar() {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <div className={cn(
      "flex flex-col bg-white border-r border-gray-200 transition-all duration-300",
      isCollapsed ? "w-16" : "w-64"
    )}>
      {/* Logo */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!isCollapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
              <Phone className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-semibold text-gray-900">AcuBat</div>
              <div className="text-xs text-gray-500">Pricing Platform</div>
            </div>
          </div>
        )}
        {isCollapsed && (
          <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center mx-auto">
            <Phone className="w-5 h-5 text-white" />
          </div>
        )}
      </div>

      {/* User Profile */}
      {!isCollapsed && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-700">A</span>
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900">Administrador</div>
              <div className="text-xs text-gray-500">admin@acubat.com</div>
            </div>
            <div className="relative">
              <Bell className="w-5 h-5 text-gray-400" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
            </div>
          </div>
        </div>
      )}

      {/* Search */}
      {!isCollapsed && (
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="Buscar..."
              className="pl-10 bg-gray-50 border-gray-200"
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white"
                  : "text-gray-700 hover:bg-gray-100"
              )}
            >
              <item.icon className="w-5 h-5" />
              {!isCollapsed && (
                <div className="flex-1">
                  <div>{item.name}</div>
                  <div className="text-xs opacity-75">{item.description}</div>
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Collapse Button */}
      <div className="p-4 border-t border-gray-200">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full"
        >
          <ChevronDown className={cn(
            "w-4 h-4 transition-transform",
            isCollapsed && "rotate-180"
          )} />
          {!isCollapsed && <span className="ml-2">Colapsar</span>}
        </Button>
      </div>
    </div>
  )
}
