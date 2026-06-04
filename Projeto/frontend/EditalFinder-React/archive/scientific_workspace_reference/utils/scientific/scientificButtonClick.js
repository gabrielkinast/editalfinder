import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * Log unificado de cliques no workspace científico.
 */
export function scientificButtonClick({ action, section = null, itemId = null, label = null }) {
  logScientificWorkspace('button_click', {
    action,
    section,
    itemId,
    label,
  });
}
