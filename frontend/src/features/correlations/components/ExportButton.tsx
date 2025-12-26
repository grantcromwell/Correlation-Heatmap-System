interface ExportButtonProps {
  onExport: () => void
  disabled?: boolean
}

export default function ExportButton({ onExport, disabled }: ExportButtonProps) {
  return (
    <button
      onClick={onExport}
      disabled={disabled}
      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      Export Data
    </button>
  )
}

