'use client'
import { useRef, useState } from 'react'
import { cn } from '@/lib/utils'

interface FileUploadProps {
  accept?: string
  maxSizeMB?: number
  onFile: (file: File) => void
  label?: string
  className?: string
}

export function FileUpload({
  accept = '.zip',
  maxSizeMB = 100,
  onFile,
  label = '点击或拖拽上传文件',
  className,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const [fileName, setFileName] = useState('')

  const handleFile = (file: File) => {
    if (file.size > maxSizeMB * 1024 * 1024) {
      alert(`文件大小不能超过 ${maxSizeMB}MB`)
      return
    }
    setFileName(file.name)
    onFile(file)
  }

  return (
    <div
      className={cn(
        'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
        dragOver ? 'border-orange-400 bg-orange-50' : 'border-gray-300 hover:border-gray-400',
        className,
      )}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault()
        setDragOver(true)
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragOver(false)
        const f = e.dataTransfer.files[0]
        if (f) handleFile(f)
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0]
          if (f) handleFile(f)
        }}
      />
      {fileName ? (
        <p className="text-sm text-green-600 font-medium">✓ {fileName}</p>
      ) : (
        <p className="text-sm text-gray-500">
          {label}
          <br />
          <span className="text-xs text-gray-400">
            支持 {accept}，最大 {maxSizeMB}MB
          </span>
        </p>
      )}
    </div>
  )
}
