# Fixture 01 — basic pair (prettify expected)

**원본** (`src/cart.ts:42`):
```ts
const total=items.reduce((acc,x)=>acc+x.price,0);
```

**수정 후**:
```ts
const total=items.reduce((acc,x)=>acc+(x.price??0),0);
```

## 변경이력
<!-- empty -->
