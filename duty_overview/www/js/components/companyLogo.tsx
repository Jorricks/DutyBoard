interface Props {
  maxHeight: number;
  maxWidth: number;
}

const CompanyLogo = ({ maxHeight, maxWidth }: Props) => {
  return (
    <img
      src={process.env.API_ADDRESS + "company_logo.png"}
      alt="Logo"
      style={{ maxHeight: maxHeight, maxWidth: maxWidth }}
    />
  );
};

export default CompanyLogo;
