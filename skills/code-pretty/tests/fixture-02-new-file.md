# Fixture 02 — new file (no original)

**수정 후** (new file: `src/cart-helpers.ts`):
```ts
export function safeReduce<T>(  arr:T[],fn:(a:number,t:T)=>number,init:number ){return arr.reduce(fn,init);}
```

## 변경이력
<!-- empty -->
