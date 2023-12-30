interface LinkProps {
  href: string; // Required - links with no `href` are not accessible
  external?: boolean;
  children: string | HTMLElement | JSX.Element;
  onClick?: JSX.MouseEventHandler<HTMLAnchorElement>;
}

const ExternalLink = ({
  children,
  href,
  external,
  onClick,
}: LinkProps) => {
  const target = external ? '_blank' : '_self';
  // Protect older browsers - see https://mathiasbynens.github.io/rel-noopener
  const rel = external && 'external noopener noreferrer';

  return (
    <a href={href} target={target} rel={rel} onClick={onClick}>
      <span className="link__text">{children}</span>
    </a>
  );
};

export default ExternalLink;
