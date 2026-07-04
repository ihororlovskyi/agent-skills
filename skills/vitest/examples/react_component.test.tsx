import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StatusBadge } from '../src/StatusBadge'

describe('StatusBadge', () => {
  it('shows the current status', () => {
    render(<StatusBadge status="Ready" />)

    expect(screen.getByText('Ready')).toBeInTheDocument()
  })
})

