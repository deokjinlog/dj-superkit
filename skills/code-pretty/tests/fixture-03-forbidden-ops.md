# Fixture 03 — forbidden refactors must NOT happen

**수정 후**:
```ts
function priceOf(x: Item) {
  if (x.tier === 1) {
    if (x.discount) {
      return x.price * 0.9;
    }
    return x.price;
  }
  return x.price * 1.1;
}
```

## 변경이력
<!-- empty -->
