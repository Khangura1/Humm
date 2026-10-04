type HummingbirdProps = {
  size?: number;
  className?: string;
};

// A hummingbird in profile facing left: long beak, raised wing, forked tail
export default function Hummingbird({ size = 96, className }: HummingbirdProps) 
{
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 128 128"
      role="img"
      aria-label="Humm hummingbird logo"
    >
      {/* beak */}
      <path d="M6 50 L40 55 L40 59 Z" fill="currentColor" />
      {/* back wing, slightly lighter for depth */}
      <path
        d="M64 52 C70 30 84 14 104 6 C98 22 90 38 78 54 Z"
        fill="currentColor"
        opacity="0.55"
      />
      {/* head and body */}
      <path
        d="M38 56 C38 46 46 41 54 42 C62 43 66 48 70 54
           C80 60 92 70 100 84 C92 84 80 80 70 76
           C58 72 46 68 41 62 C39 60 38 58 38 56 Z"
        fill="currentColor"
      />
      {/* forked tail */}
      <path d="M96 78 L122 104 L104 86 L114 116 L92 84 Z" fill="currentColor" />
      {/* front wing */}
      <path
        d="M58 50 C62 28 74 10 92 0 C90 20 84 38 72 58 Z"
        fill="currentColor"
      />
      {/* eye */}
      <circle cx="49" cy="50" r="2.6" style={{ fill: "var(--eye, #f4ead8)" }} />
    </svg>
  );
}