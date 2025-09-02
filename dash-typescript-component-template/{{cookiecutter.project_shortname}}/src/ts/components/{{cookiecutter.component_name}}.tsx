import React from 'react';
import {DashComponentProps} from '../props';

type Props = {
    // Insert props
} & DashComponentProps;

/**
 * Component description
 */
const {{cookiecutter.component_name}} = (props: Props) => {
    const { id } = props;
    return (
        <div id={id}>
            {/* Insert code */}
        </div>
    )
}

{{cookiecutter.component_name}}.defaultProps = {};

export default {{cookiecutter.component_name}};
