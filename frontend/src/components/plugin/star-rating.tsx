'use client'

import { useState } from 'react'
import { Star } from 'lucide-react'

interface StarRatingProps {
  value: number
  onChange?: (value: number) => void
  size?: number
  interactive?: boolean
}

export function StarRating({
  value,
  onChange,
  size = 16,
  interactive = false,
}: StarRatingProps) {
  const [hoverValue, setHoverValue] = useState(0)
  const displayValue = interactive && hoverValue > 0 ? hoverValue : value

  return (
    <div className="inline-flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = star <= Math.round(displayValue)
        return (
          <button
            key={star}
            type="button"
            disabled={!interactive}
            className={interactive ? 'cursor-pointer transition-transform hover:scale-110' : 'cursor-default'}
            onMouseEnter={() => interactive && setHoverValue(star)}
            onMouseLeave={() => interactive && setHoverValue(0)}
            onClick={() => interactive && onChange?.(star)}
          >
            <Star
              style={{ width: size, height: size }}
              className={
                filled
                  ? 'fill-amber-400 text-amber-400'
                  : 'text-gray-300'
              }
            />
          </button>
        )
      })}
    </div>
  )
}
