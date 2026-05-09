# Fixture 05 — already clean (byte-identical expected)

**수정 후**:
```ts
export function totalPrice(items: Item[]): number {
  return items.reduce((acc, item) => acc + (item.price ?? 0), 0);
}
```

## 변경이력
<!-- empty -->
