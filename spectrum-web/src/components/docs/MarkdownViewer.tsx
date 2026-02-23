import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { getDocumentation, type DocName } from '@/lib/api/client'
import { MermaidDiagram } from './MermaidDiagram'

interface MarkdownViewerProps {
  docName: DocName
}

export function MarkdownViewer({ docName }: MarkdownViewerProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['documentation', docName],
    queryFn: () => getDocumentation(docName),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <p className="text-red-700 dark:text-red-400">
          Failed to load documentation: {error instanceof Error ? error.message : 'Unknown error'}
        </p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="p-4 text-slate-500 dark:text-slate-400">
        No content available.
      </div>
    )
  }

  return (
    <article className="prose prose-slate dark:prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Code blocks - handle mermaid specially
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            const language = match ? match[1] : ''
            const codeString = String(children).replace(/\n$/, '')

            // Render mermaid diagrams
            if (language === 'mermaid') {
              return <MermaidDiagram chart={codeString} />
            }

            // Inline code
            if (!className) {
              return (
                <code
                  className="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-sm font-mono text-slate-800 dark:text-slate-200"
                  {...props}
                >
                  {children}
                </code>
              )
            }

            // Code blocks
            return (
              <div className="relative my-4">
                {language && (
                  <div className="absolute top-0 right-0 px-2 py-1 text-xs text-slate-400 dark:text-slate-500 bg-slate-800 dark:bg-slate-900 rounded-bl">
                    {language}
                  </div>
                )}
                <pre className="p-4 bg-slate-800 dark:bg-slate-900 rounded-lg overflow-x-auto">
                  <code className="text-sm font-mono text-slate-200" {...props}>
                    {children}
                  </code>
                </pre>
              </div>
            )
          },

          // Headings with anchor links
          h1({ children }) {
            return (
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white mt-8 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
                {children}
              </h1>
            )
          },
          h2({ children }) {
            return (
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mt-8 mb-3 pb-2 border-b border-slate-200 dark:border-slate-700">
                {children}
              </h2>
            )
          },
          h3({ children }) {
            return (
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mt-6 mb-2">
                {children}
              </h3>
            )
          },
          h4({ children }) {
            return (
              <h4 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mt-4 mb-2">
                {children}
              </h4>
            )
          },

          // Paragraphs
          p({ children }) {
            return (
              <p className="my-3 text-slate-700 dark:text-slate-300 leading-relaxed">
                {children}
              </p>
            )
          },

          // Links
          a({ href, children }) {
            const isExternal = href?.startsWith('http')
            return (
              <a
                href={href}
                target={isExternal ? '_blank' : undefined}
                rel={isExternal ? 'noopener noreferrer' : undefined}
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                {children}
              </a>
            )
          },

          // Lists
          ul({ children }) {
            return (
              <ul className="my-3 pl-6 list-disc text-slate-700 dark:text-slate-300 space-y-1">
                {children}
              </ul>
            )
          },
          ol({ children }) {
            return (
              <ol className="my-3 pl-6 list-decimal text-slate-700 dark:text-slate-300 space-y-1">
                {children}
              </ol>
            )
          },
          li({ children }) {
            return <li className="leading-relaxed">{children}</li>
          },

          // Blockquotes
          blockquote({ children }) {
            return (
              <blockquote className="my-4 pl-4 border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20 py-2 italic text-slate-600 dark:text-slate-400">
                {children}
              </blockquote>
            )
          },

          // Tables
          table({ children }) {
            return (
              <div className="my-4 overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
                  {children}
                </table>
              </div>
            )
          },
          thead({ children }) {
            return (
              <thead className="bg-slate-100 dark:bg-slate-800">
                {children}
              </thead>
            )
          },
          th({ children }) {
            return (
              <th className="px-4 py-2 text-left text-sm font-semibold text-slate-900 dark:text-white">
                {children}
              </th>
            )
          },
          td({ children }) {
            return (
              <td className="px-4 py-2 text-sm text-slate-700 dark:text-slate-300 border-t border-slate-200 dark:border-slate-700">
                {children}
              </td>
            )
          },

          // Horizontal rule
          hr() {
            return <hr className="my-8 border-slate-200 dark:border-slate-700" />
          },

          // Strong and emphasis
          strong({ children }) {
            return <strong className="font-semibold text-slate-900 dark:text-white">{children}</strong>
          },
          em({ children }) {
            return <em className="italic">{children}</em>
          },
        }}
      >
        {data.content}
      </ReactMarkdown>
    </article>
  )
}
