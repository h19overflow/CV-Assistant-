import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  diagram: string;
  className?: string;
}

export const MermaidDiagram: React.FC<MermaidDiagramProps> = ({
  diagram,
  className = '',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !diagram) return;

    // Initialize Mermaid
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
      },
    });

    // Generate unique ID for this diagram
    const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Render the diagram
    const renderDiagram = async () => {
      try {
        const { svg } = await mermaid.render(id, diagram);
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (error) {
        console.error('Error rendering Mermaid diagram:', error);
        if (containerRef.current) {
          containerRef.current.innerHTML = `
            <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              <p class="font-medium">Error rendering diagram</p>
              <p class="text-sm mt-1">Please check the diagram syntax</p>
            </div>
          `;
        }
      }
    };

    renderDiagram();
  }, [diagram]);

  return (
    <div
      ref={containerRef}
      className={`mermaid-container overflow-auto ${className}`}
      style={{ minHeight: '200px' }}
    />
  );
};