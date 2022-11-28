interface Props {
  maxHeight: number;
  maxWidth: number;
}


const CompanyLogo = ({maxHeight, maxWidth}: Props) => {
  return (
    <img src="http://localhost:8000/company_logo.png" alt="Logo" style={{maxHeight:maxHeight, maxWidth:maxWidth}} />
  )
};

export default CompanyLogo;