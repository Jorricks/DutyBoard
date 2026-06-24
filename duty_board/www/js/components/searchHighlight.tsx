import {Box} from "@chakra-ui/react";
import {getHighlightParts} from "../utils/search";

interface Props {
  searchTerms?: string[];
  text: string;
}

export default function SearchHighlight({searchTerms = [], text}: Props) {
  const parts = getHighlightParts(text, searchTerms);

  return (
    <>
      {parts.map((part, index) => (
        part.highlighted ? (
          <Box as="mark" bg="yellow.200" borderRadius="sm" color="inherit" key={index} px="1px">
            {part.text}
          </Box>
        ) : part.text
      ))}
    </>
  );
}
