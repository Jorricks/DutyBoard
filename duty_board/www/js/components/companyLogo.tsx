interface Props {
  maxHeight: number;
  maxWidth: number;
}

const CompanyLogo = ({ maxHeight, maxWidth }: Props) => {
  return (
    <img
      src={import.meta.env.VITE_API_ADDRESS + "company_logo.png"}
      alt="Logo"
      style={{ maxHeight: maxHeight, maxWidth: maxWidth }}
    />
  );
};

export default CompanyLogo;
