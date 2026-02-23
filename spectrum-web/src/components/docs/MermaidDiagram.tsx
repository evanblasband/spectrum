import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

interface MermaidDiagramProps {
  chart: string
}

// Initialize mermaid with high-contrast theme settings
mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    // Background - ensure light backgrounds throughout
    background: '#ffffff',
    mainBkg: '#ffffff',
    secondBkg: '#f8fafc',

    // Primary nodes (blue) - white text on blue
    primaryColor: '#3b82f6',
    primaryTextColor: '#ffffff',
    primaryBorderColor: '#1e40af',

    // Secondary nodes - white text on slate
    secondaryColor: '#475569',
    secondaryTextColor: '#ffffff',
    secondaryBorderColor: '#334155',

    // Tertiary nodes - dark text on light background
    tertiaryColor: '#e2e8f0',
    tertiaryTextColor: '#0f172a',
    tertiaryBorderColor: '#94a3b8',

    // Default text - very dark for contrast
    textColor: '#0f172a',

    // Node text colors
    nodeTextColor: '#0f172a',

    // Lines
    lineColor: '#475569',

    // Flowchart specific
    nodeBorder: '#1e40af',
    clusterBkg: '#f1f5f9',
    clusterBorder: '#94a3b8',
    defaultLinkColor: '#475569',
    titleColor: '#0f172a',
    edgeLabelBackground: '#ffffff',

    // Subgraph/cluster labels - dark text
    subgraphTitleColor: '#0f172a',

    // Notes - dark text on amber
    noteBkgColor: '#fef3c7',
    noteTextColor: '#78350f',
    noteBorderColor: '#d97706',

    // Sequence diagram
    actorBkg: '#3b82f6',
    actorTextColor: '#ffffff',
    actorBorder: '#1e40af',
    actorLineColor: '#475569',
    signalColor: '#0f172a',
    signalTextColor: '#0f172a',
    labelTextColor: '#0f172a',
    labelBoxBkgColor: '#ffffff',
    labelBoxBorderColor: '#94a3b8',
    loopTextColor: '#0f172a',
    activationBkgColor: '#dbeafe',
    activationBorderColor: '#3b82f6',
    sequenceNumberColor: '#ffffff',

    // Class diagram
    classText: '#0f172a',

    // State diagram
    labelColor: '#0f172a',
    altBackground: '#f1f5f9',

    // Pie chart - ensure good contrast with light legend background
    pie1: '#1e40af',
    pie2: '#ea580c',
    pie3: '#475569',
    pie4: '#15803d',
    pie5: '#ca8a04',
    pie6: '#7c3aed',
    pie7: '#be185d',
    pieTextColor: '#ffffff',
    pieTitleTextColor: '#0f172a',
    pieSectionTextColor: '#ffffff',
    pieLegendTextColor: '#0f172a',
    pieLegendTextSize: '14px',
    pieStrokeColor: '#ffffff',
    pieStrokeWidth: '2px',
    pieOuterStrokeWidth: '2px',
    pieOpacity: '1',

    // Git diagram
    git0: '#3b82f6',
    git1: '#f97316',
    git2: '#22c55e',
    git3: '#eab308',
    gitBranchLabel0: '#ffffff',
    gitBranchLabel1: '#ffffff',
    gitBranchLabel2: '#ffffff',
    gitBranchLabel3: '#0f172a',

    // ER diagram
    attributeBackgroundColorOdd: '#f8fafc',
    attributeBackgroundColorEven: '#e2e8f0',

    // Fonts
    fontFamily: 'system-ui, -apple-system, sans-serif',
    fontSize: '14px',
  },
  flowchart: {
    curve: 'basis',
    padding: 20,
    htmlLabels: true,
    useMaxWidth: true,
  },
  securityLevel: 'loose',
})

let diagramId = 0

export function MermaidDiagram({ chart }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const renderDiagram = async () => {
      if (!containerRef.current) return

      try {
        const id = `mermaid-${diagramId++}`
        const { svg: renderedSvg } = await mermaid.render(id, chart)
        setSvg(renderedSvg)
        setError(null)
      } catch (err) {
        console.error('Mermaid rendering error:', err)
        setError(err instanceof Error ? err.message : 'Failed to render diagram')
      }
    }

    renderDiagram()
  }, [chart])

  if (error) {
    return (
      <div className="my-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <p className="text-sm text-red-700 dark:text-red-400 mb-2">
          Failed to render diagram: {error}
        </p>
        <pre className="text-xs text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 p-2 rounded overflow-x-auto">
          {chart}
        </pre>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className="my-6 p-4 bg-white rounded-lg border border-slate-200 dark:border-slate-600 overflow-x-auto"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
}
