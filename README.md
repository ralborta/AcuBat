# 🚀 Backend Acubat - Sistema de Gestión de Productos

Sistema backend profesional para procesamiento de archivos Excel con lógica de negocio, visualización moderna y alertas inteligentes.

## 🎯 Características

- ✅ Carga y procesamiento de archivos Excel
- ✅ Aplicación automática de markup por canal y marca
- ✅ Redondeo inteligente de precios
- ✅ Panel web moderno con filtros
- ✅ Sistema de alertas con colores e iconos
- ✅ Integración con OpenAI para validaciones inteligentes
- ✅ API REST completa con FastAPI

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd acubat-backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus claves de OpenAI
```

5. **Ejecutar el servidor**
```bash
uvicorn api.main:app --reload
```

## 📁 Estructura del Proyecto

```
acubat-backend/
├── api/
│   ├── main.py         # Backend FastAPI (endpoints)
│   ├── logic.py        # Reglas de negocio (markup, redondeo, margen)
│   ├── parser.py       # Lectura de Excel y normalización
│   ├── openai_helper.py # Funciones para razonamiento con OpenAI
│   └── models.py       # Representación de producto, canal, alerta
├── data/               # Archivos fuente (lista_moura.xlsx, etc.)
├── templates/          # HTML con Bootstrap
├── static/             # CSS y JS
├── requirements.txt
└── README.md
```

## 🚀 Uso

1. **Acceder al panel web**: http://localhost:8000
2. **Subir archivo Excel**: Usar el formulario de carga
3. **Ver productos**: Tabla con filtros y alertas
4. **API endpoints**: http://localhost:8000/docs

## 🔧 Configuración

### Variables de Entorno (.env)
```
OPENAI_API_KEY=tu_clave_de_openai
DATABASE_URL=sqlite:///./acubat.db
DEBUG=True
```

## 📊 Lógica de Negocio

- **Markup por canal**: Minorista (35%), Mayorista (25%), Distribuidor (15%)
- **Redondeo**: Solo minoristas, múltiplos de $100
- **Alertas**: Márgenes bajos, productos sin código, precios liberados

## 🤖 Integración OpenAI

El sistema utiliza OpenAI para:
- Detectar inconsistencias en datos
- Sugerir márgenes óptimos
- Clasificar productos automáticamente
- Generar alertas inteligentes

## 🔄 Próximas Funcionalidades

- [ ] Integración con Make.com para automatización
- [ ] Notificaciones por WhatsApp/Email
- [ ] Dashboard con métricas
- [ ] Exportación a PDF/Excel
- [ ] Sistema de usuarios y permisos 