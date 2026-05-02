import React, { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

const ExpandableSection = ({
  title,
  subtitle,
  children,
  defaultOpen = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultOpen);

  return (
    <div className="border border-gray-200 rounded-xl mb-3 bg-white shadow-sm overflow-hidden transition-all">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex justify-between items-center p-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div>
          <span className="font-semibold text-gray-800">{title}</span>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        )}
      </button>
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-gray-100">{children}</div>
      )}
    </div>
  );
};

export default ExpandableSection;
