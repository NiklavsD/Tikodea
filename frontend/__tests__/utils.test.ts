import { cn, formatDate, formatNumber } from '../src/lib/utils';

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', true && 'visible')).toBe('base visible');
  });
});

describe('formatNumber', () => {
  it('returns dash for null', () => {
    expect(formatNumber(null)).toBe('-');
  });

  it('formats millions', () => {
    expect(formatNumber(1500000)).toBe('1.5M');
  });

  it('formats thousands', () => {
    expect(formatNumber(1500)).toBe('1.5K');
  });

  it('returns small numbers as-is', () => {
    expect(formatNumber(999)).toBe('999');
  });
});

describe('formatDate', () => {
  it('formats ISO date string', () => {
    const result = formatDate('2024-03-15T12:00:00Z');
    expect(result).toContain('Mar');
    expect(result).toContain('15');
    expect(result).toContain('2024');
  });
});
