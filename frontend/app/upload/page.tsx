'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/hooks/use-toast'
import { Upload, FileSpreadsheet, ArrowRight, CheckCircle } from 'lucide-react'
import { useDropzone } from 'react-dropzone'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const { toast } = useToast()
  const router = useRouter()

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0]
      if (selectedFile.type.includes('spreadsheet') || selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls')) {
        setFile(selectedFile)
        toast({
          title: "Archivo seleccionado",
          description: `${selectedFile.name} está listo para subir`,
        })
      } else {
        toast({
          title: "Tipo de archivo no válido",
          description: "Solo se permiten archivos Excel (.xlsx, .xls)",
          variant: "destructive",
        })
      }
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
  })

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
                        formData.append('tenant_id', 'acubat-tenant-id') // TODO: Get from context

                      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/upload`, {
          method: 'POST',
          headers: {
            'x-api-key': process.env.NEXT_PUBLIC_API_KEY || ''
          },
          body: formData,
        })

      if (response.ok) {
        const result = await response.json()
        setUploadResult(result)
        setUploaded(true)
        toast({
          title: "¡Archivo subido exitosamente!",
          description: `${result.normalized_items_count} productos procesados`,
        })
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Error al subir archivo')
      }
    } catch (error) {
      toast({
        title: "Error al subir archivo",
        description: error instanceof Error ? error.message : "Error desconocido",
        variant: "destructive",
      })
    } finally {
      setUploading(false)
    }
  }

  const handleSimulate = () => {
    if (uploadResult) {
      // Navegar a la página de simulación con los datos
      router.push(`/simulate?list_id=${uploadResult.id}`)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Carga de Archivos</h1>
        <p className="text-gray-600">Sube archivos Excel con listas de precios para procesar</p>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileSpreadsheet className="w-5 h-5" />
            <span>Subir Archivo Excel</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            {isDragActive ? (
              <p className="text-blue-600">Suelta el archivo aquí...</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">
                  Arrastra y suelta un archivo Excel aquí, o haz clic para seleccionar
                </p>
                <p className="text-sm text-gray-500">
                  Formatos soportados: .xlsx, .xls
                </p>
              </div>
            )}
          </div>

          {/* File Info */}
          {file && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium text-green-800">{file.name}</p>
                  <p className="text-sm text-green-600">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Upload Button */}
          {file && !uploaded && (
            <Button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Subiendo...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Subir Archivo
                </>
              )}
            </Button>
          )}

          {/* Upload Result */}
          {uploaded && uploadResult && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-blue-800">Archivo procesado exitosamente</h3>
                  <p className="text-sm text-blue-600">
                    {uploadResult.normalized_items_count} productos normalizados
                  </p>
                </div>
                <Button onClick={handleSimulate} className="bg-blue-600 hover:bg-blue-700">
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Simular Precios
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Instrucciones</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-gray-600">
            <p>El archivo Excel debe contener las siguientes columnas:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li><strong>SKU:</strong> Código del producto</li>
              <li><strong>Marca:</strong> Marca del producto (ej: Moura)</li>
              <li><strong>Línea:</strong> Línea del producto (ej: Automotriz, Pesada)</li>
              <li><strong>Precio Base:</strong> Precio de lista</li>
              <li><strong>Costo:</strong> Costo del producto</li>
            </ul>
            <p className="mt-4 text-xs text-gray-500">
              Los nombres de las columnas pueden variar. El sistema detectará automáticamente
              las columnas equivalentes (ej: &quot;codigo&quot; = SKU, &quot;precio_lista&quot; = Precio Base).
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
