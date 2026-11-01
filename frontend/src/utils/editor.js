import { CommentKit, Markdown } from 'frappe-ui/editor'

// Feature request descriptions: text formatting only, stored as markdown.
// No uploads, mentions or tags.
export const DESCRIPTION_EXTENSIONS = [
  CommentKit.configure({ image: false, video: false, attachment: false, mention: false, tag: false }),
  Markdown,
]
