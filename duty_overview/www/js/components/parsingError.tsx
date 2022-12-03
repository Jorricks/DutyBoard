import { Box, Heading } from "@chakra-ui/react";
import { GiTerror } from '@react-icons/all-files/gi/GiTerror';


const ParsingError = ({
  errorDescription, error
}: {errorDescription: string, error: string}) => {

  return (
    <Box textAlign="center" py={4} px={4}>
      <Heading as="h2" size="2xl" color={'red.300'} textAlign={'center'}>
        <GiTerror style={{marginLeft: "auto", marginRight: "auto"}}/>
      </Heading>
      <Heading as="h2" size="l" mt={6} mb={2}>
        {errorDescription}
      </Heading>
      <Box className="code-snippet">
        <Box className="code">
          {error}
        </Box>
      </Box>
    </Box>
  );
}

export default ParsingError;