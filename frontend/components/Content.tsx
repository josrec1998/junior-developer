
type Source = {
  id: string;
  title: string;
  source: string;
  favicon: string | null;
};

type Data = {
  category: string;
  question: string;
  content: string;
  sources: Source[];
};

export default function Content({ item }: { item: Data }) {
  return (
    <article className="w-full rounded-lg border border-white/40 p-6">
      <p className="mb-3 text-sm capitalize opacity-75">
        {item.category.replaceAll("_", " ")}
      </p>

      <h3 className="mb-3 text-lg font-semibold">
        {item.question}
      </h3>

      <div
        className="mb-5 space-y-3 leading-relaxed"
        dangerouslySetInnerHTML={{ __html: item.content }}
      />

      <h4 className="mb-3 font-semibold">Sources</h4>

      <ul className="space-y-3">
        {item.sources.map((source) => (
          <li key={source.id} className="flex items-start gap-3">
            {source.favicon && (
              <img
                src={source.favicon}
                alt=""
                width={20}
                height={20}
                className="mt-1 h-5 w-5 shrink-0"
              />
            )}

            <a
              href={source.source}
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:opacity-75"
            >
              {source.title}
            </a>
          </li>
        ))}
      </ul>
    </article>
  );
}
