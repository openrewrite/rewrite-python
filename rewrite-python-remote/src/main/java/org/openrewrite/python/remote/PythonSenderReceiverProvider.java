/*
 * Copyright 2024 the original author or authors.
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.openrewrite.python.remote;

import com.google.auto.service.AutoService;
import org.openrewrite.python.tree.Py;
import org.openrewrite.remote.Receiver;
import org.openrewrite.remote.Sender;
import org.openrewrite.remote.SenderReceiverProvider;
import org.openrewrite.remote.Validator;

@AutoService(SenderReceiverProvider.class)
public class PythonSenderReceiverProvider implements SenderReceiverProvider<Py> {
    @Override
    public Class<Py> getType() {
        return Py.class;
    }

    @Override
    public Sender<Py> newSender() {
        return new PythonSender();
    }

    @Override
    public Receiver<Py> newReceiver() {
        return new PythonReceiver();
    }

    @Override
    public Validator newValidator() {
        return Validator.fromVisitor(new PythonValidator<>());
    }
}
